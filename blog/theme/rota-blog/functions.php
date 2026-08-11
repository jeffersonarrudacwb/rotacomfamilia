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

/*
 * NOTA SOBRE AS FONTES
 *
 * Playfair Display e Inter NÃO são carregadas por este tema. Elas vêm da
 * Biblioteca de Fontes do WordPress (Aparência → Fontes), que baixa os
 * arquivos uma vez e os serve de wp-content/uploads/fonts/. Continuam
 * hospedadas no nosso servidor: nenhuma chamada ao Google em tempo de
 * execução, o que mantém a conformidade com a LGPD.
 *
 * A primeira versão deste tema declarava as fontes no theme.json com caminhos
 * relativos (file:./assets/fonts/...). Não funcionou: num tema-filho, o
 * WordPress resolveu esses caminhos contra a pasta do tema PAI, gerando cinco
 * @font-face apontando para arquivos que nunca existiriam. As declarações
 * foram removidas.
 *
 * O theme.json continua declarando as famílias (slugs serif/sans/mono), porque
 * é delas que saem as variáveis --wp--preset--font-family--* usadas nos
 * templates. O @font-face casa por NOME da família, não por slug — então
 * "Playfair Display" no theme.json encontra o @font-face que a Biblioteca
 * publica com esse mesmo nome.
 *
 * Se um dia as fontes sumirem do site, o lugar de olhar é
 * Aparência → Fontes → Biblioteca, não este arquivo.
 */
