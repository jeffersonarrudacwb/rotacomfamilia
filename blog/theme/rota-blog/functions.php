<?php
/**
 * Rota com Família — Blog
 * Tema-filho do Twenty Twenty-Five.
 *
 * Aqui só entra o que o theme.json não resolve. A regra de ouro deste arquivo:
 * se der para fazer no theme.json, faça lá — de lá o Editor de Site oferece a
 * opção visualmente para a Kharol, e daqui não.
 */

if (!defined('ABSPATH')) {
    exit;
}

/**
 * Carrega o style.css do filho depois do CSS do pai.
 *
 * Tema de blocos não carrega o style.css do filho sozinho em toda situação,
 * então declaramos explicitamente. A dependência em 'twentytwentyfive-style'
 * garante a ordem: primeiro o pai, depois o nosso, senão o nosso perde.
 */
add_action('wp_enqueue_scripts', function () {
    wp_enqueue_style(
        'rota-blog',
        get_stylesheet_directory_uri() . '/style.css',
        ['twentytwentyfive-style'],
        wp_get_theme()->get('Version')
    );
});

/**
 * O mesmo CSS também no editor, para a Kharol escrever vendo o resultado real.
 * Sem isso, o texto no editor sai com a fonte e o espaçamento do tema pai, e a
 * pessoa formata no escuro.
 */
add_action('after_setup_theme', function () {
    add_editor_style('style.css');
});

/**
 * Remove o autor do resumo dos posts na listagem.
 *
 * Numa família de três pessoas, "por Kharol" em todo post não informa nada —
 * e o nome do autor é justamente o que a gente acabou de tirar da API pública.
 * Não faz sentido fechar a porta e deixar a janela aberta.
 */
add_filter('body_class', function ($classes) {
    $classes[] = 'rota-blog';
    return $classes;
});

/**
 * Comprimento do resumo automático.
 *
 * O padrão do WordPress é 55 palavras, que na listagem em cartão estoura o
 * espaço e desalinha os cartões. 28 cabe em três linhas na maioria das telas.
 */
add_filter('excerpt_length', function () {
    return 28;
}, 999);

add_filter('excerpt_more', function () {
    return '…';
});

/**
 * Título da aba do navegador nas páginas de arquivo.
 *
 * O Yoast cuida disso nos posts, mas nos arquivos de categoria o padrão fica
 * "Categoria: Nome — Site". Encurtar ajuda quem tem muitas abas abertas.
 */
add_filter('get_the_archive_title_prefix', '__return_empty_string');

/**
 * Aviso no painel se as fontes locais não estiverem instaladas.
 *
 * O theme.json aponta para arquivos em assets/fonts/. Se eles não existirem, o
 * blog continua funcionando com Georgia e a fonte do sistema — não quebra, mas
 * deixa de parecer com o site. Um aviso visível evita que isso passe batido
 * por meses.
 */
add_action('admin_notices', function () {
    if (!current_user_can('manage_options')) {
        return;
    }

    $pasta = get_stylesheet_directory() . '/assets/fonts/';
    $necessarias = [
        'playfair-display-700.woff2',
        'playfair-display-800.woff2',
        'inter-400.woff2',
        'inter-600.woff2',
        'inter-700.woff2',
    ];

    $faltando = [];
    foreach ($necessarias as $arquivo) {
        if (!file_exists($pasta . $arquivo)) {
            $faltando[] = $arquivo;
        }
    }

    if (empty($faltando)) {
        return;
    }

    echo '<div class="notice notice-warning"><p><strong>Rota com Família:</strong> ';
    echo esc_html(count($faltando)) . ' arquivo(s) de fonte não encontrado(s) em ';
    echo '<code>wp-content/themes/rota-blog/assets/fonts/</code>. ';
    echo 'O blog está funcionando, mas usando fontes de reserva — a tipografia não ';
    echo 'está igual à do site. Faltando: <code>';
    echo esc_html(implode('</code>, <code>', $faltando));
    echo '</code>.</p></div>';
});
