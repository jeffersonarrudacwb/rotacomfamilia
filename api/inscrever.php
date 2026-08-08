<?php
/**
 * Rota com Família — ponte de inscrição para o Brevo
 * -----------------------------------------------------------------------------
 * Por que este arquivo existe:
 *
 * O site é estático. Se o JavaScript chamasse a API do Brevo direto do
 * navegador, a chave de API ficaria visível para qualquer visitante em
 * Ctrl+U, e quem a copiasse poderia enviar email em nome do domínio. Além
 * disso, o endpoint de formulário do Brevo não devolve cabeçalho CORS, então
 * o navegador rejeitaria a resposta e o site diria "não conseguimos enviar"
 * mesmo com o cadastro tendo entrado — a pessoa tentaria de novo e duplicaria.
 *
 * Este arquivo resolve os dois: roda no servidor, onde CORS não existe e onde
 * a chave fica fora do alcance do visitante.
 *
 * A chave NÃO fica aqui. Fica em rota-config.php, um nível ACIMA de
 * public_html, fora do alcance do navegador e fora do deploy — o FTP publica
 * apenas dentro de public_html, então nenhuma publicação sobrescreve esse
 * arquivo, e ele nunca entra no Git.
 * -----------------------------------------------------------------------------
 */

declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store');

/** Responde e encerra. Mensagens em português: vão direto para a tela. */
function responder(int $http, bool $ok, string $mensagem, array $extra = []): void
{
    http_response_code($http);
    echo json_encode(
        array_merge(['ok' => $ok, 'mensagem' => $mensagem], $extra),
        JSON_UNESCAPED_UNICODE
    );
    exit;
}

// ---------------------------------------------------------------------------
// 1. Só aceita POST
// ---------------------------------------------------------------------------
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Allow: POST');
    responder(405, false, 'Método não permitido.');
}

// ---------------------------------------------------------------------------
// 2. Carrega a configuração de fora do public_html
// ---------------------------------------------------------------------------
$candidatos = [
    __DIR__ . '/../../rota-config.php',   // /home/USUARIO/rota-config.php  <- recomendado
    __DIR__ . '/../rota-config.php',      // dentro de public_html (pior, mas funciona)
];

$config = null;
foreach ($candidatos as $caminho) {
    if (is_file($caminho)) {
        /** @var array $config */
        $config = require $caminho;
        break;
    }
}

if (!is_array($config) || empty($config['api_key'])) {
    // Sem configuração o site ainda funciona: o JavaScript cai no modo
    // "cadastro manual por email", que é honesto. Não fingimos sucesso.
    error_log('[rota] inscrever.php: rota-config.php ausente ou sem api_key');
    responder(503, false, 'Cadastro automático ainda não configurado.', ['configurar' => true]);
}

$API_KEY   = (string) $config['api_key'];
$LISTAS    = is_array($config['listas'] ?? null) ? $config['listas'] : [];
$LISTA_PAD = (int) ($config['lista_padrao'] ?? 0);

// ---------------------------------------------------------------------------
// 3. Lê o corpo — aceita JSON e formulário tradicional
// ---------------------------------------------------------------------------
$bruto = file_get_contents('php://input') ?: '';
$dados = json_decode($bruto, true);
if (!is_array($dados)) {
    $dados = $_POST;
}

$email  = strtolower(trim((string) ($dados['email'] ?? '')));
$nome   = trim((string) ($dados['nome'] ?? ''));
$origem = trim((string) ($dados['origem'] ?? 'desconhecida'));
$isca   = trim((string) ($dados['rcf_site_extra'] ?? ''));   // honeypot

// ---------------------------------------------------------------------------
// 4. Honeypot.
//
//    O formulário do site NUNCA manda este campo: o rota-forms.js já barra o
//    bot no navegador e retorna antes de montar o envio. A checagem aqui cobre
//    outro caso: um robô que leia o rota-forms.js, descubra este endereço e
//    faça POST direto preenchendo todos os campos que achou no HTML.
//
//    Responde sucesso de propósito, para o robô não descobrir que foi barrado.
//    É o único ponto em que a resposta não reflete a realidade, e é intencional.
//    Contra POST direto sem esse campo, quem protege é o freio por IP do item 6.
// ---------------------------------------------------------------------------
if ($isca !== '') {
    responder(200, true, 'Inscrição recebida.');
}

// ---------------------------------------------------------------------------
// 5. Validação
// ---------------------------------------------------------------------------
if ($email === '' || !filter_var($email, FILTER_VALIDATE_EMAIL) || strlen($email) > 180) {
    responder(422, false, 'Endereço de email inválido.');
}
$nome   = mb_substr($nome, 0, 80);
$origem = preg_replace('/[^a-z0-9 _\-]/i', '', mb_substr($origem, 0, 40)) ?: 'desconhecida';

// ---------------------------------------------------------------------------
// 6. Freio por IP. Sem isto, o endpoint é público e alguém poderia enchê-lo
//    de cadastros falsos. 5 tentativas a cada 10 minutos resolve sem
//    incomodar ninguém de verdade.
// ---------------------------------------------------------------------------
$ip = (string) ($_SERVER['REMOTE_ADDR'] ?? '0.0.0.0');
$marca = sys_get_temp_dir() . '/rota_lead_' . sha1($ip);
$janela = 600;
$limite = 5;

$batidas = [];
if (is_file($marca)) {
    $lido = json_decode((string) file_get_contents($marca), true);
    if (is_array($lido)) {
        $agora = time();
        $batidas = array_values(array_filter(
            $lido,
            static fn($t) => is_int($t) && ($agora - $t) < $janela
        ));
    }
}
if (count($batidas) >= $limite) {
    responder(429, false, 'Muitas tentativas. Aguarde alguns minutos e tente de novo.');
}
$batidas[] = time();
@file_put_contents($marca, json_encode($batidas), LOCK_EX);

// ---------------------------------------------------------------------------
// 7. Envia para o Brevo
// ---------------------------------------------------------------------------
$listaId = (int) ($LISTAS[$origem] ?? $LISTA_PAD);
if ($listaId <= 0) {
    error_log('[rota] inscrever.php: nenhuma lista configurada para a origem ' . $origem);
    responder(503, false, 'Cadastro automático ainda não configurado.', ['configurar' => true]);
}

$atributos = [
    // Registro do consentimento — é a evidência que a LGPD pede.
    'ORIGEM'           => $origem,
    'CONSENT_DATA'     => gmdate('Y-m-d H:i:s') . ' UTC',
    'CONSENT_IP'       => $ip,
];
if ($nome !== '') {
    $atributos['NOME'] = $nome;
}

$corpo = json_encode([
    'email'         => $email,
    'attributes'    => $atributos,
    'listIds'       => [$listaId],
    // Se já existir, atualiza em vez de devolver erro de duplicado. Sem isto,
    // quem se cadastra duas vezes vê uma mensagem de erro sem motivo.
    'updateEnabled' => true,
], JSON_UNESCAPED_UNICODE);

$ch = curl_init('https://api.brevo.com/v3/contacts');
curl_setopt_array($ch, [
    CURLOPT_POST           => true,
    CURLOPT_POSTFIELDS     => $corpo,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT        => 12,
    CURLOPT_CONNECTTIMEOUT => 6,
    CURLOPT_HTTPHEADER     => [
        'accept: application/json',
        'content-type: application/json',
        'api-key: ' . $API_KEY,
    ],
]);
$resposta = curl_exec($ch);
$status   = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
$erroCurl = curl_error($ch);
curl_close($ch);

if ($resposta === false) {
    error_log('[rota] inscrever.php: falha de rede com o Brevo: ' . $erroCurl);
    responder(502, false, 'Não conseguimos concluir agora. Tente de novo em alguns instantes.');
}

// 201 = contato criado · 204 = contato já existia e foi atualizado
if ($status === 201 || $status === 204 || $status === 200) {
    responder(200, true, 'Inscrição confirmada. Confira sua caixa de entrada.');
}

// Erro do Brevo. O detalhe vai para o log do servidor, nunca para a tela: a
// resposta pode conter informação da conta.
error_log('[rota] inscrever.php: Brevo devolveu ' . $status . ' -> ' . (string) $resposta);

if ($status === 401) {
    responder(503, false, 'Cadastro automático indisponível.', ['configurar' => true]);
}
responder(502, false, 'Não conseguimos concluir agora. Tente de novo em alguns instantes.');
