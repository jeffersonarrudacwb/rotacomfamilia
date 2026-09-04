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

    /* -----------------------------------------------------------------------
     * db — o banco da área de acompanhamento do cliente
     *
     * Como criar, no cPanel → "Bancos de Dados MySQL":
     *
     *   1. "Criar Novo Banco de Dados": nome curto, ex. "rota". O cPanel
     *      prefixa sozinho e ele vira jeffe095_rota.
     *   2. "Adicionar Novo Usuário": use a senha gerada pelo próprio painel,
     *      não invente uma. Copie na hora.
     *   3. "Adicionar Usuário ao Banco de Dados" → marque TODOS OS PRIVILÉGIOS.
     *      O cPanel não oferece permissão por tabela, então é tudo ou nada.
     *   4. Rode o sql/schema.sql do repositório no phpMyAdmin, nesse banco.
     *
     * DEIXE "MySQL Remoto" VAZIO no cPanel. Não há motivo para este banco
     * aceitar conexão de fora do próprio servidor, e cada host liberado ali é
     * uma porta a mais para uma senha que vive num arquivo de texto.
     * ----------------------------------------------------------------------- */
    'db' => [
        'host'    => 'localhost',
        'nome'    => 'jeffe095_rota',
        'usuario' => 'jeffe095_rota',
        'senha'   => 'COLE_A_SENHA_GERADA_PELO_CPANEL',
    ],

    /* -----------------------------------------------------------------------
     * pimenta — o segredo que protege os códigos de acompanhamento
     *
     * O banco não guarda o código do cliente em claro. Guarda
     * SHA-256(pimenta . codigo). Esta string é o que torna um vazamento do
     * banco inútil: sem ela, os códigos têm 50 bits e cairiam todos em algumas
     * horas de GPU. Com ela aqui fora, o dump sozinho não vale nada.
     *
     * Como gerar (rode uma vez e cole o resultado):
     *     php -r "echo bin2hex(random_bytes(32)), PHP_EOL;"
     *
     * NUNCA troque depois que houver código emitido. Trocar a pimenta invalida
     * todos os códigos de uma vez, e não há como recuperá-los: seria preciso
     * emitir e reenviar um novo para cada cliente.
     * ----------------------------------------------------------------------- */
    'pimenta' => 'COLE_AQUI_64_CARACTERES_HEXADECIMAIS',

    /* -----------------------------------------------------------------------
     * token_export — a sua chave para ler o que os clientes marcaram
     *
     * A área não tem tela de administração, por escolha. Este token é como
     * você lê as respostas, sem depender de MySQL remoto:
     *
     *     curl -s https://rotacomfamilia.com.br/api/acompanhamento.php \
     *          -H "Content-Type: application/json" \
     *          -d '{"acao":"exportar","token":"...","codigo":"..."}'
     *
     * O MESMO token abre o diagnóstico, que é como você descobre por que a
     * área não está funcionando sem depender do log do servidor:
     *
     *     -d '{"acao":"diagnostico","token":"..."}'
     *
     * Ele diz onde achou este arquivo, se conectou no banco e por que não, se
     * as 8 tabelas existem e quantas linhas têm. Passando também um "codigo",
     * responde se a pimenta daqui é a mesma que gerou aquele código.
     *
     * Isso existe porque o log não estava acessível: rotacomfamilia.com.br é
     * domínio ADICIONAL, e a página de Erros do cPanel mostra o log do domínio
     * PRINCIPAL da conta, não o nosso.
     *
     * Gere do mesmo jeito da pimenta. É segredo de administrador: não vai para
     * o WhatsApp do cliente, não vai para o navegador, não vai para o Git.
     * ----------------------------------------------------------------------- */
    'token_export' => 'COLE_AQUI_OUTROS_64_CARACTERES_HEXADECIMAIS',
];
