<?php
/**
 * numeros.php — os numeros das redes para o midia kit.
 * -----------------------------------------------------------------------------
 * Devolve o conteudo de dados/numeros-redes.json, com o YouTube atualizado
 * na hora quando ha chave de API configurada.
 *
 * POR QUE ISTO EXISTE
 *
 * O midia kit mostra numeros de audiencia para marcas. Numero velho em midia
 * kit e pior do que numero nenhum: a marca abre o canal, ve outro valor e
 * passa a duvidar do resto do documento.
 *
 * O QUE E AUTOMATICO E O QUE NAO E
 *
 *   YouTube    automatico. A API de dados v3 devolve inscritos, videos e
 *              views totais com uma chave simples, sem OAuth e sem token que
 *              expira. Cota de 10.000 unidades por dia; esta chamada custa 1.
 *
 *   Instagram  nao. Exige conta comercial ligada a uma pagina do Facebook, um
 *              app na Meta e um token de longa duracao que vence em 60 dias e
 *              precisa ser renovado. Enquanto isso nao existir, o numero vem
 *              digitado do JSON, com a data em que foi conferido.
 *
 *   TikTok     nao. Exige app registrado e aprovado pela TikTok.
 *
 * Isso esta dito em voz alta porque a alternativa e alguem daqui a seis meses
 * achar que o Instagram se atualiza sozinho e deixar o numero envelhecer.
 *
 * SE ESTE ARQUIVO FALHAR, A PAGINA NAO QUEBRA
 *
 * O mediakit.html ja nasce com os numeros escritos no HTML e so os substitui
 * se a resposta daqui vier boa. Sem PHP, sem chave ou sem internet, o visitante
 * ve os numeros do JSON. Ninguem ve "..." nem caixa vazia.
 * -----------------------------------------------------------------------------
 */

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
// Cinco minutos de cache no navegador: o numero nao muda de minuto em minuto,
// e isso evita bater no arquivo a cada carregamento de pagina.
header('Cache-Control: public, max-age=300');

$RAIZ  = __DIR__ . '/..';
$FONTE = $RAIZ . '/dados/numeros-redes.json';

/** Devolve o JSON e encerra. */
function entregar(array $dados, string $origem): void
{
    $dados['_origem'] = $origem;
    echo json_encode($dados, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

$base = is_readable($FONTE) ? json_decode(file_get_contents($FONTE), true) : null;

if (!is_array($base)) {
    // Sem o arquivo base nao ha o que entregar. 503 e nao 500: e falta de
    // recurso, e o front ja sabe cair para os numeros do HTML.
    http_response_code(503);
    echo json_encode(['erro' => 'fonte indisponivel'], JSON_UNESCAPED_UNICODE);
    exit;
}

/* ---------------------------------------------------------------------------
 * Chave da API. Mesmo caminho que o inscrever.php usa: o arquivo real mora
 * ACIMA da pasta do site, onde o navegador nao alcanca e o FTP do deploy nao
 * escreve.
 * ------------------------------------------------------------------------ */
$chave = '';
foreach ([__DIR__ . '/../../rota-config.php', __DIR__ . '/../rota-config.php'] as $caminho) {
    if (is_readable($caminho)) {
        $config = require $caminho;
        if (is_array($config) && !empty($config['youtube_api_key'])) {
            $chave = (string) $config['youtube_api_key'];
        }
        break;
    }
}

$canal = $base['redes']['youtube']['canal_id'] ?? '';

if ($chave === '' || $canal === '') {
    // Configuracao incompleta e situacao normal, nao erro: o site funciona
    // assim ate a chave ser criada. Entrega os numeros digitados.
    entregar($base, 'json');
}

/* ---------------------------------------------------------------------------
 * Cache em disco. Sem ele, uma pagina compartilhada no Instagram e vista mil
 * vezes numa tarde gastaria mil unidades de cota por nada.
 * ------------------------------------------------------------------------ */
$CACHE     = sys_get_temp_dir() . '/rota-youtube.json';
$VALIDADE  = 6 * 3600;

if (is_readable($CACHE) && (time() - filemtime($CACHE)) < $VALIDADE) {
    $guardado = json_decode(file_get_contents($CACHE), true);
    if (is_array($guardado)) {
        entregar(aplicar($base, $guardado), 'cache');
    }
}

/**
 * Troca os valores do YouTube pelos que vieram da API.
 * Metrica que a API nao devolveu fica com o valor digitado.
 */
function aplicar(array $base, array $api): array
{
    foreach ($base['redes']['youtube']['metricas'] as $i => $m) {
        $c = $m['chave'] ?? '';
        if (isset($api[$c]) && is_numeric($api[$c])) {
            $base['redes']['youtube']['metricas'][$i]['valor'] = (int) $api[$c];
        }
    }
    $base['redes']['youtube']['verificado_em'] = date('Y-m-d');
    return $base;
}

/* --------------------------------------------------------------------------- */

$url = 'https://www.googleapis.com/youtube/v3/channels'
     . '?part=statistics&id=' . urlencode($canal) . '&key=' . urlencode($chave);

$resposta = false;

if (function_exists('curl_init')) {
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        // Cinco segundos e o limite: se a API do Google estiver lenta, o
        // visitante nao pode esperar por ela. Ele ja tem numero na tela.
        CURLOPT_TIMEOUT        => 5,
        CURLOPT_CONNECTTIMEOUT => 3,
        CURLOPT_SSL_VERIFYPEER => true,
    ]);
    $resposta = curl_exec($ch);
    if (curl_getinfo($ch, CURLINFO_RESPONSE_CODE) !== 200) {
        $resposta = false;
    }
    curl_close($ch);
}

$json = $resposta ? json_decode($resposta, true) : null;
$est  = $json['items'][0]['statistics'] ?? null;

if (!is_array($est)) {
    error_log('[rota] numeros.php: YouTube nao respondeu como esperado');
    // Cache velho vale mais do que numero digitado ha meses.
    if (is_readable($CACHE)) {
        $guardado = json_decode(file_get_contents($CACHE), true);
        if (is_array($guardado)) {
            entregar(aplicar($base, $guardado), 'cache-vencido');
        }
    }
    entregar($base, 'json');
}

$novo = [
    'inscritos' => isset($est['subscriberCount']) ? (int) $est['subscriberCount'] : null,
    'videos'    => isset($est['videoCount'])      ? (int) $est['videoCount']      : null,
    'views'     => isset($est['viewCount'])       ? (int) $est['viewCount']       : null,
];

@file_put_contents($CACHE, json_encode($novo));

entregar(aplicar($base, $novo), 'api');
