<?php
/**
 * MODELO de configuração — NÃO é este arquivo que o site usa.
 * -----------------------------------------------------------------------------
 * COMO USAR
 *
 * 1. No cPanel, abra o Gerenciador de Arquivos e marque "Mostrar arquivos
 *    ocultos" nas configurações.
 *
 * 2. Vá para a pasta que CONTÉM a public_html — normalmente /home/SEU_USUARIO.
 *    É um nível ACIMA do site. Isso é de propósito: nada aí é acessível pelo
 *    navegador, e o deploy por FTP só escreve dentro de public_html, então
 *    nenhuma publicação vai sobrescrever este arquivo.
 *
 * 3. Crie ali um arquivo chamado exatamente:
 *        rota-config.php
 *
 * 4. Copie o conteúdo daqui para dentro dele e preencha os valores reais.
 *
 * NUNCA coloque este arquivo preenchido dentro de public_html, e nunca o
 * comite no Git. O .gitignore já bloqueia o nome rota-config.php.
 * -----------------------------------------------------------------------------
 */

return [

    /* -----------------------------------------------------------------------
     * api_key — a chave da API do Brevo
     *
     * Onde achar: entre no Brevo, clique no seu nome no canto superior
     * direito → "SMTP e API" → aba "Chaves de API" → "Gerar uma nova chave
     * de API". Dê o nome "site rotacomfamilia".
     *
     * Ela começa com xkeysib- e é mostrada UMA única vez. Copie na hora.
     * Se perder, gere outra e apague a antiga.
     * ----------------------------------------------------------------------- */
    'api_key' => 'xkeysib-COLE_A_SUA_CHAVE_AQUI',

    /* -----------------------------------------------------------------------
     * listas — para qual lista do Brevo vai cada formulário do site
     *
     * A chave à esquerda é o valor do atributo data-origem do <form> no HTML.
     * O número à direita é o ID da lista no Brevo.
     *
     * Onde achar o ID: Brevo → Contatos → Listas. O número aparece na coluna
     * "ID", e também no fim da URL ao abrir a lista.
     *
     * Crie duas listas no Brevo:
     *   "Newsletter — Guia de Milhas"   -> use o ID em newsletter
     *   "Lista de espera — Cursos"      -> use o ID em curso
     * ----------------------------------------------------------------------- */
    'listas' => [
        'newsletter' => 0,   // troque pelo ID real
        'curso'      => 0,   // troque pelo ID real
    ],

    /* -----------------------------------------------------------------------
     * lista_padrao — usada quando a origem não estiver no mapa acima.
     * Deixe apontando para a lista da newsletter.
     * ----------------------------------------------------------------------- */
    'lista_padrao' => 0,
];
