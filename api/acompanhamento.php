<?php
/**
 * Rota com Família — área de acompanhamento do cliente
 * -----------------------------------------------------------------------------
 * O cliente digita o código do orçamento e vê o planejamento dele: descrição,
 * voos e as atrações que eu cadastrei por cidade. Marca o que quer, diz quantas
 * pessoas vão, e pode acrescentar atração que não estava na lista.
 *
 * POR QUE UM ARQUIVO SÓ, E NÃO TRÊS
 *
 * O gerar-deploy.py tem uma lista explícita de arquivos, e o
 * conferir_referencias() valida só src=, href= e srcset=. A URL de um endpoint
 * mora dentro de um fetch(), que é invisível para ele. Ou seja: esquecer um
 * arquivo PHP na lista do deploy passa no build, passa na CI, sobe o site, e só
 * aparece como 404 na hora em que o cliente clica em salvar. Cada arquivo a
 * mais é mais uma chance disso. Um arquivo, uma linha na lista, um alvo de
 * php -l. O despacho é pelo campo "acao" do corpo.
 *
 * O QUE ESTE ARQUIVO NÃO FAZ, E É DE PROPÓSITO
 *
 * Não cai para $_POST como o inscrever.php faz. Aqui é exigido
 * Content-Type: application/json, e só php://input é lido. Isso obriga preflight
 * em qualquer fetch de outra origem — e como nunca respondemos preflight, a
 * classe inteira de requisição cross-origin "simples" deixa de existir. Custa
 * um if.
 *
 * Não tem honeypot. Lá ele existe porque é formulário público que robô acha.
 * Aqui é preciso um segredo de 50 bits, que robô nenhum tem. Honeypot só
 * acrescentaria um caminho onde o endpoint mente para quem chamou, que é a
 * última coisa que se quer num endpoint que grava.
 *
 * O CÓDIGO É A CREDENCIAL
 *
 * Não há login. O código do orçamento é a senha, e por isso:
 *   - nunca entra na URL (só corpo de POST), para não cair no log do Apache,
 *     no histórico do navegador nem num print de tela;
 *   - é guardado no banco como SHA-256(pimenta . código), com a pimenta no
 *     rota-config.php, fora da raiz do site;
 *   - nunca vai para o error_log. Quando preciso identificar, uso os 8
 *     primeiros caracteres do hash.
 *
 * A configuração e a senha do banco ficam em rota-config.php, um nível ACIMA
 * de public_html, fora do alcance do navegador e fora do deploy.
 * -----------------------------------------------------------------------------
 */

declare(strict_types=1);

/* -----------------------------------------------------------------------------
 * 0. Antes de qualquer coisa: não vazar o DSN
 *
 * Este é o primeiro PHP do repositório que segura senha de banco, e a mensagem
 * de exceção do construtor do PDO traz host, banco e usuário dentro dela. Se
 * display_errors estiver ligado na hospedagem — o que acontece, e não é coisa
 * que o repositório controle —, um PDOException não capturado imprime isso na
 * tela do visitante.
 * -------------------------------------------------------------------------- */
ini_set('display_errors', '0');
ini_set('log_errors', '1');

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store');
header('X-Robots-Tag: noindex, nofollow');

/** Responde e encerra. As mensagens vão direto para a tela do cliente. */
function responder(int $http, bool $ok, string $mensagem, array $extra = []): void
{
    http_response_code($http);
    echo json_encode(
        array_merge(['ok' => $ok, 'mensagem' => $mensagem], $extra),
        JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES
    );
    exit;
}

set_exception_handler(function (Throwable $e): void {
    error_log('[rota] acompanhamento: ' . $e->getMessage()
              . ' @ ' . $e->getFile() . ':' . $e->getLine());
    responder(503, false,
        'O sistema está fora do ar neste momento. Tente de novo em alguns '
        . 'minutos, ou me chame no WhatsApp.',
        ['configurar' => true]);
});

/**
 * Acha e lê o rota-config.php. Devolve [config, caminho] ou [null, null].
 *
 * É função, e não código solto, porque o diagnóstico precisa fazer a MESMA
 * busca que o fluxo normal. Duas buscas separadas divergem com o tempo, e um
 * diagnóstico que procura em outro lugar mente justo no dia em que é preciso.
 */
function carregar_config(): array
{
    foreach ([__DIR__ . '/../../rota-config.php',   // recomendado
              __DIR__ . '/../rota-config.php'] as $caminho) {
        if (is_file($caminho)) {
            $c = require $caminho;
            return [is_array($c) ? $c : null, $caminho];
        }
    }
    return [null, null];
}

// ---------------------------------------------------------------------------
// 1. Constantes
// ---------------------------------------------------------------------------

/** Crockford base32 sem I, L, O e U. 32 símbolos, 10 posições = 50 bits. */
const RCF_ALFABETO = '0123456789ABCDEFGHJKMNPQRSTVWXYZ';
const RCF_TAM_CODIGO = 10;

/**
 * As únicas etapas em que o cliente pode gravar.
 *
 * Fica numa constante só. Duas cópias desta lista é como a trava acaba
 * divergindo entre a tela e o servidor.
 */
const RCF_ETAPAS_EDITAVEIS = ['hospedagem', 'atracoes'];

const RCF_JANELA_SEG    = 600;  // 10 minutos
const RCF_LIMITE_ABRIR  = 10;   // falhas de código por IP
const RCF_LIMITE_SALVAR = 60;   // gravações por IP
const RCF_LIMITE_GLOBAL = 60;   // falhas de código no site inteiro
const RCF_ESPERA_GLOBAL = 60;   // segundos de descanso quando o global estoura

const RCF_MAX_NOME      = 120;
const RCF_MAX_DESCRICAO = 500;
const RCF_MAX_ESCOLHAS  = 400;
const RCF_MAX_NOVAS     = 30;

// ---------------------------------------------------------------------------
// 2. Só POST, e só JSON
// ---------------------------------------------------------------------------
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Allow: POST');
    responder(405, false, 'Método não permitido.');
}

$tipo = $_SERVER['CONTENT_TYPE'] ?? $_SERVER['HTTP_CONTENT_TYPE'] ?? '';
if (stripos($tipo, 'application/json') === false) {
    responder(415, false, 'Envie o corpo como application/json.');
}

$bruto = file_get_contents('php://input');
if ($bruto === false || $bruto === '' || strlen($bruto) > 300000) {
    responder(400, false, 'Corpo vazio ou grande demais.');
}
$dados = json_decode($bruto, true);
if (!is_array($dados)) {
    responder(400, false, 'Corpo não é um JSON válido.');
}

$acao = (string) ($dados['acao'] ?? '');
if (!in_array($acao, ['abrir', 'salvar', 'exportar', 'diagnostico'], true)) {
    responder(400, false, 'Ação desconhecida.');
}

/* -----------------------------------------------------------------------------
 * 2b. diagnostico: por que isto não está funcionando
 *
 * Nasceu de uma noite perdida. A área subiu, a página abriu, e o endpoint
 * respondeu "o sistema está fora do ar" sem dizer mais nada, que é o
 * comportamento certo para o visitante e péssimo para quem instalou. O motivo
 * real ia para o error_log, e o error_log de um domínio ADICIONAL não é o que a
 * página de Erros do cPanel mostra: ela mostra o do domínio principal da conta.
 * A informação existia e não havia como chegar nela pelo painel.
 *
 * Roda ANTES da checagem de formato do código e ANTES da conexão, e abre o
 * banco por conta própria dentro de try/catch. Tem que ser assim: o que se quer
 * diagnosticar é justamente a conexão que falha, e o fluxo normal morre nela
 * antes de conseguir contar o que houve.
 *
 * O QUE ELE NÃO REVELA SEM O TOKEN
 *
 * Sem configuração, ou sem token_export dentro dela, responde exatamente a
 * mesma frase do fluxo normal e para por aí. Sem esse cuidado, um varredor
 * descobriria pelo endpoint se o servidor tem configuração, o nome do banco e a
 * versão do MySQL, coisas que hoje ele não tem como saber.
 * -------------------------------------------------------------------------- */
if ($acao === 'diagnostico') {
    [$cfg, $de_onde] = carregar_config();

    $token = is_array($cfg) ? (string) ($cfg['token_export'] ?? '') : '';
    if ($token === '') {
        // Mesma resposta do fluxo normal: nada de novo vaza.
        responder(503, false,
            'A área de acompanhamento ainda não está configurada.',
            ['configurar' => true]);
    }
    if (!hash_equals($token, (string) ($dados['token'] ?? ''))) {
        responder(401, false, 'Token inválido.');
    }

    $L = [];
    $L[] = 'ARQUIVO DE CONFIGURAÇÃO';
    $L[] = '  achado em .............. ' . $de_onde;
    $L[] = '  tem db ................. ' . (empty($cfg['db']) ? 'NÃO' : 'sim');
    $L[] = '  tem pimenta ............ ' . (empty($cfg['pimenta']) ? 'NÃO' : 'sim');
    // O tamanho, e nunca o valor. A pimenta não sai daqui por porta nenhuma.
    $L[] = '  tamanho da pimenta ..... '
           . strlen((string) ($cfg['pimenta'] ?? '')) . ' caracteres, esperado 64';
    $L[] = '  tem api_key do Brevo ... ' . (empty($cfg['api_key']) ? 'NÃO' : 'sim')
           . '   <- se vier NÃO, o arquivo foi sobrescrito';
    $L[] = '';
    $L[] = 'SERVIDOR';
    $L[] = '  PHP .................... ' . PHP_VERSION;
    $L[] = '  extensão pdo_mysql ..... '
           . (extension_loaded('pdo_mysql') ? 'sim' : 'NÃO, e sem ela nada roda');
    $L[] = '';
    $L[] = 'BANCO';
    $L[] = '  host ................... ' . ($cfg['db']['host'] ?? '(vazio)');
    $L[] = '  nome ................... ' . ($cfg['db']['nome'] ?? '(vazio)');
    $L[] = '  usuário ................ ' . ($cfg['db']['usuario'] ?? '(vazio)');
    $L[] = '  senha preenchida ....... '
           . (($cfg['db']['senha'] ?? '') === '' ? 'NÃO' : 'sim');

    try {
        $conn = new PDO(
            sprintf('mysql:host=%s;dbname=%s;charset=utf8mb4',
                    $cfg['db']['host'] ?? 'localhost', $cfg['db']['nome'] ?? ''),
            (string) ($cfg['db']['usuario'] ?? ''),
            (string) ($cfg['db']['senha'] ?? ''),
            [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
             PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC]
        );
        $L[] = '  conectou ............... SIM';
        $L[] = '  versão do servidor ..... '
               . $conn->query('SELECT VERSION()')->fetchColumn();
    } catch (Throwable $e) {
        // A mensagem do PDO é justamente o que faltava. Sai só para quem tem o
        // token, e é o único ponto do endpoint onde erro interno aparece.
        $L[] = '  conectou ............... NÃO';
        $L[] = '  motivo ................. ' . $e->getMessage();
        $L[] = '';

        /* O conselho por CÓDIGO, e não um texto só para toda falha.
         *
         * A primeira versão disto dizia "é o usuário não ligado ao banco" para
         * qualquer erro de conexão, e mandou para o lado errado no primeiro uso
         * real: o erro era 1045, e 1045 não é isso. Os dois se parecem na tela
         * e pedem consertos diferentes.
         *
         *   1045  autenticação falhou. Usuário ou senha errados.
         *   1044  autenticou, mas não tem direito NESTE banco. Aí sim é o
         *         passo "Adicionar Usuário ao Banco de Dados".
         *   1049  o banco não existe com esse nome.
         *   2002  não chegou no servidor. Host errado.
         */
        $msg = $e->getMessage();
        if (strpos($msg, '[1045]') !== false) {
            $L[] = '1045 é senha ou usuário errado, e NÃO é falta de permissão.';
            $L[] = 'O jeito confiável: cPanel > Bancos de Dados MySQL > na lista';
            $L[] = 'de usuários, "Alterar Senha". Gere uma nova e cole aqui.';
            $L[] = '';
            $L[] = 'Ao gerar, abra "Opções avançadas" e peça uma senha só com';
            $L[] = 'letras e números. Senha com barra invertida ou apóstrofo';
            $L[] = 'quebra em silêncio dentro das aspas do PHP, e some espaço no';
            $L[] = 'fim quando se cola do painel.';
        } elseif (strpos($msg, '[1044]') !== false) {
            $L[] = '1044 é o usuário sem direito NESTE banco. A senha está certa.';
            $L[] = 'No cPanel, "Adicionar Usuário ao Banco de Dados" é um passo à';
            $L[] = 'parte de criar os dois, e marque TODOS OS PRIVILÉGIOS.';
        } elseif (strpos($msg, '[1049]') !== false) {
            $L[] = '1049 é banco inexistente. Confira o nome: o cPanel prefixa';
            $L[] = 'com a conta, então "rota" vira "jeffe095_rota".';
        } elseif (strpos($msg, '[2002]') !== false
                  || strpos($msg, '[2003]') !== false) {
            $L[] = 'Não chegou no servidor de banco. Em hospedagem compartilhada';
            $L[] = 'o host é "localhost", e não um endereço de fora.';
        }
        responder(200, true, 'Diagnóstico.', ['relatorio' => implode("\n", $L)]);
    }

    $L[] = '';
    $L[] = 'TABELAS';
    $esperadas = ['rcf_planejamento', 'rcf_voo', 'rcf_cidade', 'rcf_atracao',
                  'rcf_escolha', 'rcf_salvamento', 'rcf_freio', 'rcf_tentativa'];
    $existem = $conn->query("SHOW TABLES LIKE 'rcf\\_%'")
                    ->fetchAll(PDO::FETCH_COLUMN);
    $faltando = array_values(array_diff($esperadas, $existem));
    foreach ($esperadas as $t) {
        if (in_array($t, $existem, true)) {
            // O nome vem da lista fixa acima, nunca da requisição: não há como
            // um nome de tabela vindo de fora entrar nesta string.
            $n = (int) $conn->query('SELECT COUNT(*) FROM `' . $t . '`')
                            ->fetchColumn();
            $L[] = sprintf('  %-18s %6d linha%s', $t, $n, $n === 1 ? '' : 's');
        } else {
            $L[] = sprintf('  %-18s FALTANDO', $t);
        }
    }
    if ($faltando) {
        $L[] = '';
        $L[] = 'Importe o sql/schema.sql no phpMyAdmin, DENTRO do banco: clique';
        $L[] = 'nele na coluna da esquerda antes de abrir a aba Importar.';
    }

    // A pergunta que mais custa tempo: a pimenta daqui é a mesma que gerou o
    // seed? Só dá para responder testando um código de verdade.
    if (!empty($dados['codigo']) && !$faltando) {
        $L[] = '';
        $L[] = 'CÓDIGO DE TESTE';
        $cod = normalizar_codigo((string) $dados['codigo']);
        if ($cod === null) {
            $L[] = '  formato ................ inválido, nem chegou a consultar';
        } else {
            $st = $conn->prepare(
                'SELECT apelido, etapa, expira_em, codigo_revogado_em'
                . ' FROM rcf_planejamento WHERE codigo_hash = ?');
            $st->execute([hash_codigo($cod, (string) $cfg['pimenta'])]);
            $achou = $st->fetch();
            if ($achou) {
                $L[] = '  encontrou .............. SIM, a pimenta bate';
                $L[] = '  apelido ................ ' . $achou['apelido'];
                $L[] = '  etapa .................. ' . $achou['etapa']
                       . (in_array($achou['etapa'], RCF_ETAPAS_EDITAVEIS, true)
                          ? '   (aceita gravação)' : '   (só leitura)');
                $L[] = '  expira em .............. '
                       . ($achou['expira_em'] ?? 'sem prazo');
                $L[] = '  revogado ............... '
                       . ($achou['codigo_revogado_em'] ?? 'não');
            } else {
                $L[] = '  encontrou .............. NÃO';
                $L[] = '';
                $L[] = 'Com as tabelas carregadas, isto quer dizer que a pimenta';
                $L[] = 'deste servidor é diferente da que gerou o seed. Rode o';
                $L[] = 'seed-acompanhamento.py de novo com a pimenta daqui e';
                $L[] = 'reimporte o SQL.';
            }
        }
    }

    responder(200, true, 'Diagnóstico.', ['relatorio' => implode("\n", $L)]);
}

/* -----------------------------------------------------------------------------
 * 3. O formato do código, ANTES de abrir o banco
 *
 * Fica aqui em cima por dois motivos que só apareceram testando:
 *
 *   1. Código com formato errado não precisa de banco nenhum para ser recusado.
 *      Deixar a checagem depois do PDO faz cada tentativa lixo abrir uma
 *      conexão à toa, que é justamente o que um varredor produz aos milhares.
 *
 *   2. Com o banco fora do ar, quem digitou o código errado recebia "o sistema
 *      está fora do ar" em vez de "esse código não tem o formato certo". A
 *      segunda frase é a verdadeira, e é a única com a qual a pessoa consegue
 *      fazer alguma coisa.
 *
 * A normalização não gasta entropia: I, L e O não existem no alfabeto, então
 * mapeá-los para 1, 1 e 0 só absorve a confusão de quem lê o código em voz alta
 * no telefone ou copia de um print.
 * -------------------------------------------------------------------------- */
$codigo = normalizar_codigo((string) ($dados['codigo'] ?? ''));
if ($codigo === null) {
    // Não gasta o freio: é um código que quem tentou já sabia ser inválido.
    responder(422, false,
        'Esse código não tem o formato certo. São 10 caracteres, como no '
        . 'exemplo que eu te mandei.');
}

// ---------------------------------------------------------------------------
// 4. Configuração, de fora do public_html
// ---------------------------------------------------------------------------
[$config, $config_de] = carregar_config();
if (!is_array($config) || empty($config['db']) || empty($config['pimenta'])) {
    error_log('[rota] acompanhamento: rota-config.php ausente ou sem db/pimenta');
    responder(503, false,
        'A área de acompanhamento ainda não está configurada.',
        ['configurar' => true]);
}

$pimenta = (string) $config['pimenta'];
$db      = $config['db'];

// ---------------------------------------------------------------------------
// 4. Banco
// ---------------------------------------------------------------------------
$pdo = new PDO(
    sprintf('mysql:host=%s;dbname=%s;charset=utf8mb4',
            $db['host'] ?? 'localhost', $db['nome'] ?? ''),
    (string) ($db['usuario'] ?? ''),
    (string) ($db['senha'] ?? ''),
    [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        // O controle de injeção que importa. Com emulação desligada, o valor
        // nunca entra na string de SQL: o servidor recebe a instrução e os
        // parâmetros separados.
        PDO::ATTR_EMULATE_PREPARES   => false,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_STRINGIFY_FETCHES  => false,
    ]
);

// ---------------------------------------------------------------------------
// 5. Auxiliares
// ---------------------------------------------------------------------------

/**
 * Deixa o código na forma canônica, ou devolve null se não puder ser um código.
 *
 * I, L e O não existem no alfabeto, então mapeá-los para 1, 1 e 0 não custa
 * entropia nenhuma e absorve quase toda confusão de quem lê um código em voz
 * alta no telefone ou copia de um print.
 */
function normalizar_codigo(string $bruto): ?string
{
    $c = strtoupper(trim($bruto));
    $c = preg_replace('/[^0-9A-Z]/', '', $c) ?? '';
    $c = strtr($c, ['I' => '1', 'L' => '1', 'O' => '0']);
    if (strlen($c) !== RCF_TAM_CODIGO) {
        return null;
    }
    if (strspn($c, RCF_ALFABETO) !== RCF_TAM_CODIGO) {
        return null;
    }
    return $c;
}

function hash_codigo(string $codigo, string $pimenta): string
{
    return hash('sha256', $pimenta . '|codigo|' . $codigo, true);
}

/**
 * A chave do freio, a partir do IP.
 *
 * REMOTE_ADDR e nada mais. X-Forwarded-For é escrito por quem chama e confiar
 * nele transforma o limitador em enfeite.
 *
 * IPv6 é reduzido ao /64, que é o menor bloco que um assinante residencial
 * costuma controlar. Sem isso, um /64 dá 1,8 x 10^19 "IPs" distintos e o
 * limitador é contornado por completo.
 */
function chave_ip(string $sufixo, string $pimenta): string
{
    $ip  = (string) ($_SERVER['REMOTE_ADDR'] ?? '0.0.0.0');
    $bin = @inet_pton($ip);
    if ($bin === false) {
        $bin = $ip;
    } elseif (strlen($bin) === 16) {
        $bin = substr($bin, 0, 8);
    }
    return hash('sha256', $pimenta . '|freio|' . $sufixo . '|' . $bin, true);
}

function hash_ip(string $pimenta): string
{
    $ip  = (string) ($_SERVER['REMOTE_ADDR'] ?? '0.0.0.0');
    $bin = @inet_pton($ip);
    return hash('sha256', $pimenta . '|ip|' . ($bin === false ? $ip : $bin), true);
}

/**
 * Soma uma batida e devolve quantas há na janela.
 *
 * A soma e a virada da janela acontecem numa instrução só, sob bloqueio de
 * linha do InnoDB na chave primária. É o conserto do limitador de arquivo do
 * inscrever.php, onde duas requisições simultâneas liam o mesmo valor, ambas
 * concluíam que ainda cabia, e ambas gravavam o mesmo número.
 *
 * Soma primeiro, decide depois: numa disputa de foto-finish alguém pode passar
 * uma tentativa a mais, o que é irrelevante com 50 bits de código. O que não
 * pode é uma tentativa deixar de ser contada.
 */
function bater_freio(PDO $pdo, string $chave): int
{
    $janela = (int) RCF_JANELA_SEG;
    $sql = "INSERT INTO rcf_freio (chave, janela_inicio, batidas)
            VALUES (:c, NOW(), 1)
            ON DUPLICATE KEY UPDATE
              batidas = IF(janela_inicio < NOW() - INTERVAL {$janela} SECOND,
                           1, batidas + 1),
              janela_inicio = IF(janela_inicio < NOW() - INTERVAL {$janela} SECOND,
                                 NOW(), janela_inicio)";
    $pdo->prepare($sql)->execute([':c' => $chave]);

    $st = $pdo->prepare('SELECT batidas FROM rcf_freio WHERE chave = :c');
    $st->execute([':c' => $chave]);
    return (int) ($st->fetchColumn() ?: 1);
}

function registrar_tentativa(PDO $pdo, string $pimenta, string $acao,
                             string $resultado, ?int $plan = null): void
{
    try {
        $st = $pdo->prepare(
            'INSERT INTO rcf_tentativa (ip_hash, acao, resultado, planejamento_id)
             VALUES (:ip, :a, :r, :p)');
        $st->execute([
            ':ip' => hash_ip($pimenta), ':a' => $acao,
            ':r'  => $resultado,        ':p' => $plan,
        ]);
    } catch (Throwable $e) {
        // Registro é diagnóstico, não é o serviço. Se falhar, o cliente não
        // pode ser penalizado por isso.
        error_log('[rota] acompanhamento: falha ao registrar tentativa: '
                  . $e->getMessage());
    }
}

/** Limpeza sem cron: uma vez a cada ~200 requisições, com teto por rodada. */
function faxina(PDO $pdo): void
{
    try {
        if (random_int(1, 200) !== 1) {
            return;
        }
        $pdo->exec('DELETE FROM rcf_freio
                     WHERE atualizado_em < NOW() - INTERVAL 1 DAY LIMIT 500');
        $pdo->exec('DELETE FROM rcf_tentativa
                     WHERE criado_em < NOW() - INTERVAL 90 DAY LIMIT 500');
    } catch (Throwable $e) {
        error_log('[rota] acompanhamento: faxina falhou: ' . $e->getMessage());
    }
}

/**
 * Acha o planejamento pelo código. Devolve a linha ou null.
 *
 * Uma igualdade sobre BINARY(32) indexado. Sem LIKE e sem varrer linha em PHP,
 * então não há oráculo de tempo que valha modelar.
 */
function achar_planejamento(PDO $pdo, string $hash): ?array
{
    $st = $pdo->prepare(
        'SELECT id, titulo, descricao, passageiros, etapa, versao,
                data_inicio, data_fim, codigo_revogado_em, expira_em
           FROM rcf_planejamento
          WHERE codigo_hash = :h');
    $st->execute([':h' => $hash]);
    $linha = $st->fetch();
    return $linha ?: null;
}

function esta_editavel(array $plan): bool
{
    if ($plan['codigo_revogado_em'] !== null) {
        return false;
    }
    if ($plan['expira_em'] !== null && strtotime($plan['expira_em']) < time()) {
        return false;
    }
    return in_array($plan['etapa'], RCF_ETAPAS_EDITAVEIS, true);
}

/** O planejamento inteiro, do jeito que a página consome. */
function montar_resposta(PDO $pdo, array $plan): array
{
    $pid = (int) $plan['id'];

    $st = $pdo->prepare(
        'SELECT tipo, bilhete, companhia, numero_voo, origem_iata, destino_iata,
                partida_local, chegada_local, duracao_min, observacao
           FROM rcf_voo WHERE planejamento_id = :p ORDER BY ordem');
    $st->execute([':p' => $pid]);
    $voos = $st->fetchAll();

    $st = $pdo->prepare(
        'SELECT id, nome, pais, chegada, saida, noites, nota
           FROM rcf_cidade WHERE planejamento_id = :p ORDER BY ordem');
    $st->execute([':p' => $pid]);
    $cidades = $st->fetchAll();

    $st = $pdo->prepare(
        'SELECT a.id, a.cidade_id, a.origem, a.nome, a.descricao, a.horario,
                a.preco_tipo, a.preco_texto, a.sazonal, a.janela, a.detalhes,
                a.url, e.resposta, e.pessoas
           FROM rcf_atracao a
           LEFT JOIN rcf_escolha e ON e.atracao_id = a.id
          WHERE a.planejamento_id = :p AND a.ativa = 1
          ORDER BY a.cidade_id, a.origem DESC, a.ordem, a.id');
    $st->execute([':p' => $pid]);

    $por_cidade = [];
    foreach ($st->fetchAll() as $a) {
        $por_cidade[(int) $a['cidade_id']][] = [
            'id'          => (int) $a['id'],
            'origem'      => $a['origem'],
            'nome'        => $a['nome'],
            'descricao'   => $a['descricao'],
            'horario'     => $a['horario'],
            'preco_tipo'  => $a['preco_tipo'],
            'preco_texto' => $a['preco_texto'],
            'sazonal'     => (bool) $a['sazonal'],
            'janela'      => $a['janela'],
            'detalhes'    => $a['detalhes'],
            'url'         => $a['url'],
            'escolha'     => $a['resposta'] === null ? null : [
                'resposta' => $a['resposta'],
                'pessoas'  => $a['pessoas'] === null ? null : (int) $a['pessoas'],
            ],
        ];
    }

    foreach ($cidades as &$c) {
        $c['id']       = (int) $c['id'];
        $c['noites']   = $c['noites'] === null ? null : (int) $c['noites'];
        $c['atracoes'] = $por_cidade[$c['id']] ?? [];
    }
    unset($c);

    return [
        'versao'       => (int) $plan['versao'],
        'planejamento' => [
            'titulo'      => $plan['titulo'],
            'descricao'   => $plan['descricao'],
            'passageiros' => (int) $plan['passageiros'],
            'inicio'      => $plan['data_inicio'],
            'fim'         => $plan['data_fim'],
            'etapa'       => $plan['etapa'],
            'editavel'    => esta_editavel($plan),
        ],
        'voos'    => $voos,
        'cidades' => $cidades,
    ];
}

// ---------------------------------------------------------------------------
// 6. exportar — a leitura de administrador
// ---------------------------------------------------------------------------
if ($acao === 'exportar') {
    $token = (string) ($config['token_export'] ?? '');
    $vindo = (string) ($dados['token'] ?? '');
    // hash_equals para a comparação não vazar, pelo tempo, quantos caracteres
    // iniciais estavam certos.
    if ($token === '' || !hash_equals($token, $vindo)) {
        registrar_tentativa($pdo, $pimenta, 'exportar', 'codigo_invalido');
        responder(401, false, 'Token inválido.');
    }
    // O código já veio normalizado e validado lá em cima, na seção 3.
    $plan = achar_planejamento($pdo, hash_codigo($codigo, $pimenta));
    if ($plan === null) {
        responder(404, false, 'Planejamento não encontrado.');
    }
    registrar_tentativa($pdo, $pimenta, 'exportar', 'ok', (int) $plan['id']);
    responder(200, true, 'Exportado.', montar_resposta($pdo, $plan));
}

// ---------------------------------------------------------------------------
// 8. O freio, e a busca do planejamento
// ---------------------------------------------------------------------------
if ($acao === 'salvar') {
    if (bater_freio($pdo, chave_ip('salvar', $pimenta)) > RCF_LIMITE_SALVAR) {
        header('Retry-After: 60');
        registrar_tentativa($pdo, $pimenta, 'salvar', 'bloqueado');
        responder(429, false, 'Muitas gravações seguidas. Espere um minuto.');
    }
}

$hash = hash_codigo($codigo, $pimenta);
$plan = achar_planejamento($pdo, $hash);

if ($plan === null) {
    // Só FALHA gasta o freio de abrir. Cliente recarregando a própria página
    // dez vezes nunca pode ser bloqueado.
    $porip   = bater_freio($pdo, chave_ip('abrir', $pimenta));
    $global  = bater_freio($pdo, hash('sha256', $pimenta . '|freio|global', true));
    registrar_tentativa($pdo, $pimenta, $acao, 'codigo_invalido');
    faxina($pdo);

    if ($porip > RCF_LIMITE_ABRIR) {
        header('Retry-After: ' . RCF_JANELA_SEG);
        responder(429, false,
            'Muitas tentativas com código errado. Espere alguns minutos.');
    }
    // O contador global é o que segura enumeração vinda de mil endereços
    // diferentes, que o limite por IP não pega. O descanso é curto de
    // propósito: ele também é uma alavanca de incômodo, e um minuto de espera
    // para um cliente legítimo é preço aceitável.
    if ($global > RCF_LIMITE_GLOBAL) {
        header('Retry-After: ' . RCF_ESPERA_GLOBAL);
        responder(429, false,
            'O sistema está com muitas tentativas agora. Tente daqui a pouco.');
    }
    responder(401, false,
        'Não achei esse código. Confira se digitou certo, ou me chame no '
        . 'WhatsApp que eu reenvio.');
}

$pid = (int) $plan['id'];

// ---------------------------------------------------------------------------
// 8. abrir
// ---------------------------------------------------------------------------
if ($acao === 'abrir') {
    $pdo->prepare('UPDATE rcf_planejamento
                      SET ultimo_acesso_em = NOW(), acessos = acessos + 1
                    WHERE id = :p')->execute([':p' => $pid]);
    registrar_tentativa($pdo, $pimenta, 'abrir', 'ok', $pid);
    faxina($pdo);
    // Ler é liberado em qualquer etapa. Quem já respondeu tem direito de rever
    // o que respondeu, mesmo depois que a viagem andou. O que a etapa tranca é
    // a gravação, e quem decide isso é o servidor, não o campo "editavel".
    responder(200, true, 'Planejamento carregado.', montar_resposta($pdo, $plan));
}

// ---------------------------------------------------------------------------
// 9. salvar
// ---------------------------------------------------------------------------
$envio_id = (string) ($dados['envio_id'] ?? '');
if (!preg_match('/^[0-9a-fA-F-]{16,36}$/', $envio_id)) {
    responder(422, false, 'Identificador de envio inválido.');
}
$versao_cliente = isset($dados['versao']) ? (int) $dados['versao'] : 0;

$escolhas = is_array($dados['escolhas'] ?? null) ? $dados['escolhas'] : [];
$novas    = is_array($dados['novas'] ?? null)    ? $dados['novas']    : [];
if (count($escolhas) > RCF_MAX_ESCOLHAS || count($novas) > RCF_MAX_NOVAS) {
    responder(422, false, 'Envio grande demais.');
}

$pdo->beginTransaction();
try {
    // FOR UPDATE é o que sustenta a trava. Sem ele:
    //   t0  o salvar lê etapa='atracoes'        -> liberado
    //   t1  eu mudo para 'roteiro' no phpMyAdmin
    //   t2  o salvar grava                      -> entra em planejamento fechado
    // Com o bloqueio de linha, um dos dois espera e ninguém grava fora de etapa.
    $st = $pdo->prepare(
        'SELECT id, etapa, versao, passageiros, codigo_revogado_em, expira_em
           FROM rcf_planejamento WHERE id = :p FOR UPDATE');
    $st->execute([':p' => $pid]);
    $atual = $st->fetch();

    if (!$atual || !esta_editavel($atual)) {
        $pdo->rollBack();
        registrar_tentativa($pdo, $pimenta, 'salvar', 'etapa_fechada', $pid);
        // 409 e não 403: 403 diria "você não tem acesso", e é falso — a mesma
        // credencial valia dois minutos atrás. 409 diz "o estado mudou", que é
        // o que aconteceu. A página usa isso para dizer a coisa certa e, acima
        // de tudo, para NÃO apagar o que o cliente já marcou.
        responder(409, false,
            'Este planejamento saiu da etapa de edição. Suas respostas '
            . 'continuam na tela: me chame no WhatsApp que eu registro.',
            ['motivo' => 'etapa_fechada', 'etapa' => $atual['etapa'] ?? null,
             'editavel' => false]);
    }

    // Envio repetido: a conexão caiu depois do commit e o navegador tentou de
    // novo. Sem isto, a segunda tentativa levaria uma versão velha e um 409
    // que não explica nada.
    $st = $pdo->prepare(
        'SELECT versao FROM rcf_salvamento
          WHERE planejamento_id = :p AND envio_id = :e');
    $st->execute([':p' => $pid, ':e' => $envio_id]);
    if ($repetido = $st->fetchColumn()) {
        $pdo->commit();
        responder(200, true, 'Respostas já salvas.',
            ['versao' => (int) $repetido, 'criadas' => [], 'repetido' => true]);
    }

    if ($versao_cliente > 0 && $versao_cliente !== (int) $atual['versao']) {
        $pdo->rollBack();
        registrar_tentativa($pdo, $pimenta, 'salvar', 'conflito', $pid);
        responder(409, false,
            'Alguém salvou este planejamento em outro aparelho enquanto você '
            . 'editava. Recarregue a página para ver a versão mais nova.',
            ['motivo' => 'conflito', 'versao' => (int) $atual['versao']]);
    }

    $passageiros = (int) $atual['passageiros'];
    $criadas = [];

    // ---- atrações novas, escritas pelo cliente ----------------------------
    $ins = $pdo->prepare(
        'INSERT INTO rcf_atracao
            (planejamento_id, cidade_id, origem, nome, descricao, ordem,
             criada_ip_hash)
         SELECT :p, c.id, \'cliente\', :nome, :desc, 900, :ip
           FROM rcf_cidade c
          WHERE c.id = :cid AND c.planejamento_id = :p2');
    // A cidade vem de um SELECT com planejamento_id no WHERE, então uma cidade
    // de outro cliente simplesmente não casa e nada é inserido. A chave
    // estrangeira composta da tabela é a segunda barreira, no armazenamento.
    //
    // origem é a string literal 'cliente' dentro do SQL. Nunca uma variável
    // vinda do corpo: é exatamente assim que se evita mass assignment.
    //
    // url não é aceita do cliente. href com javascript: é XSS sem precisar de
    // innerHTML nenhum.
    foreach ($novas as $n) {
        if (!is_array($n)) {
            continue;
        }
        $nome = trim((string) ($n['nome'] ?? ''));
        // Guarda CRU, tirando só controle. Escapar na entrada quebraria o PDF:
        // o build_roteiro.py passa a string para o Paragraph() do ReportLab,
        // que interpreta a própria marcação, e um "&lt;" pré-escapado sairia
        // literal no documento. Escape acontece em cada saída, não aqui.
        $nome = preg_replace('/[\x00-\x1F\x7F]/u', '', $nome) ?? '';
        if ($nome === '') {
            continue;
        }
        $nome = mb_substr($nome, 0, RCF_MAX_NOME);
        $desc = trim((string) ($n['descricao'] ?? ''));
        $desc = mb_substr(preg_replace('/[\x00-\x1F\x7F]/u', '', $desc) ?? '',
                          0, RCF_MAX_DESCRICAO);
        $cid  = (int) ($n['cidade_id'] ?? 0);
        if ($cid <= 0) {
            continue;
        }

        $ins->execute([
            ':p' => $pid, ':nome' => $nome, ':desc' => ($desc === '' ? null : $desc),
            ':ip' => hash_ip($pimenta), ':cid' => $cid, ':p2' => $pid,
        ]);
        if ($ins->rowCount() === 0) {
            continue;   // cidade não é deste planejamento
        }
        $novo_id = (int) $pdo->lastInsertId();
        // Quem acrescenta é porque quer: já nasce marcada como sim.
        $pdo->prepare(
            'INSERT INTO rcf_escolha (planejamento_id, atracao_id, resposta)
             VALUES (:p, :a, \'sim\')')->execute([':p' => $pid, ':a' => $novo_id]);
        $criadas[] = ['id' => $novo_id, 'cidade_id' => $cid, 'nome' => $nome,
                      'descricao' => ($desc === '' ? null : $desc)];
    }

    // ---- as marcações -----------------------------------------------------
    //
    // Carrego uma vez quais atrações são deste planejamento e confiro em PHP.
    // A alternativa seria um INSERT ... SELECT com ON DUPLICATE KEY UPDATE
    // usando VALUES(), que funciona mas está depreciado desde o MySQL 8.0.20 e
    // um dia deixa de existir.
    //
    // Conferir em PHP não afrouxa nada: a chave estrangeira COMPOSTA da
    // rcf_escolha, (atracao_id, planejamento_id), recusa no armazenamento
    // qualquer par que não bata. O PHP é a primeira barreira e o InnoDB é a
    // que não depende de eu ter lembrado.
    $st = $pdo->prepare(
        'SELECT id FROM rcf_atracao WHERE planejamento_id = :p AND ativa = 1');
    $st->execute([':p' => $pid]);
    $validas = array_flip(array_map('intval', $st->fetchAll(PDO::FETCH_COLUMN)));

    // Uma instrução preparada, reusada dentro da transação. Não monto lista
    // IN(...) com join de string: para 60 linhas o ganho é zero e o risco de
    // errar é real. Nomes distintos nos dois lados porque, com emulação
    // desligada, o PDO não deixa repetir um parâmetro nomeado.
    $up = $pdo->prepare(
        'INSERT INTO rcf_escolha (planejamento_id, atracao_id, resposta, pessoas)
         VALUES (:p, :aid, :r, :q)
         ON DUPLICATE KEY UPDATE resposta = :r2, pessoas = :q2');
    foreach ($escolhas as $e) {
        if (!is_array($e)) {
            continue;
        }
        $aid = (int) ($e['atracao_id'] ?? 0);
        $r   = (string) ($e['resposta'] ?? '');
        if ($aid <= 0 || !in_array($r, ['sim', 'nao'], true)) {
            continue;
        }
        if (!isset($validas[$aid])) {
            continue;   // atração de outro planejamento, ou desativada
        }
        $q = $e['pessoas'] ?? null;
        if ($q === null || $q === '' || $q === 0 || $q === '0') {
            $q = null;             // em branco = todos, que é o pedido
        } else {
            $q = (int) $q;
            // O limite que importa cruza tabela e nenhum CHECK expressa. E em
            // MySQL 5.7 o CHECK do esquema nem roda, então esta linha é a que
            // vale.
            if ($q < 1 || $q > $passageiros) {
                $pdo->rollBack();
                responder(422, false, sprintf(
                    'A quantidade de pessoas precisa estar entre 1 e %d.',
                    $passageiros));
            }
        }
        $up->execute([':p' => $pid, ':aid' => $aid,
                      ':r' => $r, ':q' => $q, ':r2' => $r, ':q2' => $q]);
    }

    $nova_versao = (int) $atual['versao'] + 1;
    $pdo->prepare('UPDATE rcf_planejamento SET versao = :v WHERE id = :p')
        ->execute([':v' => $nova_versao, ':p' => $pid]);

    $pdo->prepare(
        'INSERT INTO rcf_salvamento
            (planejamento_id, versao, envio_id, payload, ip_hash)
         VALUES (:p, :v, :e, :j, :ip)')->execute([
        ':p' => $pid, ':v' => $nova_versao, ':e' => $envio_id,
        ':j' => json_encode(['escolhas' => $escolhas, 'novas' => $novas],
                            JSON_UNESCAPED_UNICODE),
        ':ip' => hash_ip($pimenta),
    ]);

    $pdo->commit();
} catch (Throwable $e) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    throw $e;   // o set_exception_handler devolve 503 e registra
}

registrar_tentativa($pdo, $pimenta, 'salvar', 'ok', $pid);
faxina($pdo);
responder(200, true, 'Suas respostas foram salvas.',
    ['versao' => $nova_versao, 'criadas' => $criadas]);
