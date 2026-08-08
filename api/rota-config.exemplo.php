<?php
/**
 * MODELO de configuração — NÃO é este arquivo que o site usa.
 * -----------------------------------------------------------------------------
 * COMO USAR
 *
 * 1. No cPanel, abra o Gerenciador de Arquivos e marque "Mostrar arquivos
 *    ocultos" nas configurações.
 *
 * 2. Vá para a pasta HOME da conta — no nosso caso /home2/jeffe095.
 *
 *    Atenção: rotacomfamilia.com.br é um domínio ADICIONAL no cPanel, então o
 *    site NÃO fica em public_html. O layout real é:
 *
 *        /home2/jeffe095/
 *        ├── rota-config.php              <- o arquivo vai AQUI
 *        ├── public_html/                 <- outro site da conta
 *        └── rotacomfamilia.com.br/       <- nosso site (raiz do FTP de deploy)
 *            └── api/inscrever.php        <- lê a chave em ../../
 *
 *    A pasta home não é raiz de nenhum site, então nada ali é alcançável pelo
 *    navegador. E o usuário de FTP do deploy está preso dentro de
 *    rotacomfamilia.com.br/, então nenhuma publicação sobrescreve este arquivo.
 *
 * 3. Crie ali um arquivo chamado exatamente:
 *        rota-config.php
 *
 * 4. Copie o conteúdo daqui para dentro dele e preencha os valores reais.
 *
 * 5. Deixe a permissão em 0600 (só o dono lê).
 *
 * NUNCA coloque este arquivo preenchido dentro da pasta do site, e nunca o
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
     * A chave à esquerda é uma PALAVRA-CHAVE procurada dentro da origem que o
     * formulário envia. Não precisa ser o valor exato: o inscrever.php tenta
     * primeiro o nome idêntico e, se não achar, procura a chave contida na
     * origem. Isso evita quebrar tudo quando o sufixo muda no HTML.
     *
     * Hoje os dois formulários mandam:
     *     "newsletter-home"      (index.html)      -> casa com a chave newsletter
     *     "curso-espera-2026"    (cursos.html)     -> casa com a chave curso
     *
     * O número à direita é o ID da lista no Brevo. Onde achar: Brevo →
     * CRM → Listas, coluna "ID" (aparece como #4, #6...). Use só o número.
     * ----------------------------------------------------------------------- */
    'listas' => [
        'newsletter' => 4,   // Newsletter — Guia de Milhas
        'curso'      => 6,   // Lista de espera — Cursos
    ],

    /* -----------------------------------------------------------------------
     * lista_padrao — rede de segurança: usada quando a origem não casar com
     * nenhuma chave acima. Deixe apontando para a lista da newsletter, para
     * que nenhum lead se perca. Se ficar 0, o site responde que o cadastro
     * automático não está configurado.
     * ----------------------------------------------------------------------- */
    'lista_padrao' => 4,
];
