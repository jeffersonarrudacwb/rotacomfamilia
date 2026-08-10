<?php
/**
 * Plugin Name: Rota com Família — Proteções
 * Description: Fecha as portas que o WordPress deixa abertas por padrão. Instalado como mu-plugin: carrega sempre e não aparece na lista de plugins, então ninguém desativa sem querer.
 * Version: 1.0
 * Author: Rota com Família
 *
 * -----------------------------------------------------------------------------
 * ONDE ESTE ARQUIVO DEVE FICAR
 *
 *     blog/wp-content/mu-plugins/rota-hardening.php
 *
 * A pasta mu-plugins provavelmente NÃO existe ainda — crie. O "mu" é de
 * "must-use": tudo que está nessa pasta é carregado automaticamente e não pode
 * ser desativado pelo painel. É o lugar certo para proteção, porque não tem
 * como alguém desligar clicando errado.
 * -----------------------------------------------------------------------------
 */

// Bloqueia acesso direto ao arquivo.
if (!defined('ABSPATH')) {
    exit;
}

/* =============================================================================
   1. A lista de usuários deixa de ser pública
   -----------------------------------------------------------------------------
   Por padrão, /wp-json/wp/v2/users devolve o nome de login de todo autor a
   quem pedir, sem autenticação. É como publicar metade da senha: o atacante
   para de adivinhar o usuário e passa a atacar só a senha.

   Importante: bloqueamos apenas quem NÃO está logado. O editor de blocos usa
   esse endpoint para montar a lista de autores; se cortássemos para todos, a
   tela de edição quebraria.
   ============================================================================= */
add_filter('rest_endpoints', function ($endpoints) {
    if (is_user_logged_in()) {
        return $endpoints;
    }
    unset($endpoints['/wp/v2/users']);
    unset($endpoints['/wp/v2/users/(?P<id>[\d]+)']);
    return $endpoints;
});

/* =============================================================================
   2. Fim da enumeração por ?author=N
   -----------------------------------------------------------------------------
   Mesmo sem a API, /blog/?author=1 redireciona para /author/nome-do-usuario/ e
   entrega o login pela URL. Um laço de 1 a 50 mapeia a equipe inteira.
   ============================================================================= */
add_action('template_redirect', function () {
    if (is_admin() || is_user_logged_in()) {
        return;
    }
    if (isset($_GET['author']) || is_author()) {
        wp_safe_redirect(home_url('/'), 301);
        exit;
    }
});

/* =============================================================================
   3. XML-RPC desligado
   -----------------------------------------------------------------------------
   O xmlrpc.php aceita centenas de tentativas de senha em UMA única requisição,
   o que faz o limitador de login perder o efeito — ele conta requisições, não
   tentativas dentro delas. Também é usado para ataque de amplificação.

   Só faria falta se você publicasse pelo app antigo do WordPress ou por
   Jetpack. Não é o caso: a Kharol publica pelo navegador.
   ============================================================================= */
add_filter('xmlrpc_enabled', '__return_false');
add_filter('xmlrpc_methods', function () {
    return [];
});

// Remove o anúncio do XML-RPC do cabeçalho e do HTML.
add_filter('wp_headers', function ($headers) {
    unset($headers['X-Pingback']);
    return $headers;
});
remove_action('wp_head', 'rsd_link');
remove_action('wp_head', 'wlwmanifest_link');

/* =============================================================================
   4. Versão do WordPress deixa de ser anunciada
   -----------------------------------------------------------------------------
   Hoje o HTML da página diz <meta name="generator" content="WordPress 7.0.3">.
   Isso permite procurar por falhas conhecidas daquela versão exata sem nem
   testar o site. Não é proteção real — é deixar de entregar o mapa.
   ============================================================================= */
remove_action('wp_head', 'wp_generator');
add_filter('the_generator', '__return_empty_string');

// A versão também vai grudada na URL de cada CSS e JS (?ver=7.0.3).
add_filter('style_loader_src', 'rcf_remover_versao', 9999);
add_filter('script_loader_src', 'rcf_remover_versao', 9999);
function rcf_remover_versao($src)
{
    if (strpos($src, 'ver=') !== false) {
        $src = remove_query_arg('ver', $src);
    }
    return $src;
}

/* =============================================================================
   5. Mensagem de erro de login deixa de confirmar o usuário
   -----------------------------------------------------------------------------
   O padrão do WordPress responde "esse nome de usuário não existe" ou "a senha
   que você digitou para o usuário X é incorreta". A segunda confirma que o
   usuário existe. Uma mensagem única para os dois casos não entrega nada.
   ============================================================================= */
add_filter('login_errors', function () {
    return 'Não foi possível entrar. Verifique os dados e tente de novo.';
});

/* =============================================================================
   6. Sem listagem de diretório em uploads
   -----------------------------------------------------------------------------
   Hoje já responde 403, mas isso vem da configuração do servidor e pode mudar
   numa migração. Garantir aqui é barato.
   ============================================================================= */
add_action('init', function () {
    if (!is_admin() && isset($_SERVER['REQUEST_URI'])) {
        $uri = (string) $_SERVER['REQUEST_URI'];
        if (preg_match('#/wp-content/uploads/?$#', $uri)) {
            status_header(403);
            exit;
        }
    }
});
