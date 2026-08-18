/* =============================================================================
   Rota com Família — rota-forms.js
   Captura de leads honesta + eventos GA4 + banner de consentimento.

   Objetivo deste arquivo: acabar com o formulário que MENTIA (trocava o texto
   do botão para "Cheque seu email!" e jogava o lead no lixo). Aqui, ou o lead
   é enviado de verdade, ou a pessoa é avisada com todas as letras de que o
   cadastro será feito à mão.

   Dependências: nenhuma. JavaScript puro, sem build, sem framework.
   Ordem de carga: DEPOIS de script.js (veja instruções no fim do arquivo).
   ============================================================================= */
(function () {
  'use strict';

  /* ###########################################################################
     ###                                                                     ###
     ###   >>>  BLOCO DE CONFIGURAÇÃO — É AQUI QUE VOCÊ MEXE  <<<            ###
     ###                                                                     ###
     ###   Enquanto ESP_ENDPOINT estiver vazio, os formulários do site NÃO   ###
     ###   fingem sucesso: eles caem no modo "mailto" (a pessoa envia um     ###
     ###   email pedindo a inscrição e você cadastra na mão). Isso é feio,   ###
     ###   mas é honesto. Preencha as constantes abaixo para ligar o envio   ###
     ###   automático.                                                       ###
     ###                                                                     ###
     ########################################################################### */

  /* ---------------------------------------------------------------------------
     ESP_ENDPOINT — URL para onde o formulário faz POST.
     ("ESP" = Email Service Provider: Brevo, Mailchimp, ConvertKit/Kit, etc.)

     >>> LEIA ISTO ANTES DE ESCOLHER O PROVEDOR — O PROBLEMA DO CORS <<<

     Os endpoints "de incorporar formulário" que Brevo, Mailchimp e ConvertKit
     entregam foram feitos para receber o envio tradicional de um <form>, NÃO
     para receber fetch de outro domínio. Nenhum dos três devolve o cabeçalho
     Access-Control-Allow-Origin. Na prática, o navegador rejeita a chamada e
     este arquivo mostra "Não conseguimos enviar agora" MESMO QUANDO o cadastro
     entrou na lista — e aí a pessoa tenta de novo e duplica o cadastro.
     É a mentira ao contrário, e não é aceitável.

     Só existem dois caminhos que funcionam de verdade:

     (a) RECOMENDADO — uma função serverless sua no meio do caminho. Ela recebe
         o POST do site, guarda a chave de API em variável de ambiente e chama o
         provedor pelo servidor, onde CORS não existe. Netlify, Vercel e
         Cloudflare Workers têm plano gratuito suficiente para este volume.
         Aí ESP_ENDPOINT vira algo como
         "https://rotacomfamilia.com.br/.netlify/functions/inscrever".

     (b) Um serviço já pensado para site estático, que devolve CORS liberado e
         responde JSON: Formspree, Buttondown ou EmailOctopus, por exemplo.
         Nesse caso é só colar a URL do serviço aqui e funciona direto.

     Onde achar o endereço em cada serviço, se ainda assim quiser testar:

     • BREVO (ex-Sendinblue)
       Contatos → Formulários → abra um formulário → "Compartilhar" →
       "Incorporar (HTML)". O action é https://xxxxx.sibforms.com/serve/MUIF...
       Sujeito ao problema de CORS acima.

     • MAILCHIMP
       Audience → Signup forms → "Embedded form". O action é
       https://SEU-USUARIO.us21.list-manage.com/subscribe/post?u=...&id=...
       Sujeito ao problema de CORS. O endpoint /subscribe/post-json responde
       HTTP 200 mesmo em caso de erro, com {"result":"error"} no corpo — este
       arquivo já trata isso na função conferirCorpo().

     • CONVERTKIT / KIT
       Grow → Landing Pages & Forms → abra o formulário → Embed → HTML. O action
       é algo como https://app.kit.com/forms/1234567/subscriptions
       Sujeito ao problema de CORS.

     TESTE OBRIGATÓRIO antes de considerar pronto: abra o site publicado no
     domínio real (não em file:// nem em localhost), cadastre um email seu,
     e confirme que ele apareceu na lista do provedor. Se aparecer erro na tela
     mas o email entrar na lista, o problema é CORS — volte para a opção (a).

     NUNCA cole aqui uma chave de API secreta (Brevo "api-key", Mailchimp API
     key etc.). Tudo que está neste arquivo é visível para qualquer visitante
     que abrir o inspetor do navegador. Chave secreta só do lado do servidor.

     >>> ESTE SITE JÁ ESTÁ RESOLVIDO — não precisa mexer aqui. <<<

     O caminho (a) descrito acima está implementado, e em PHP em vez de função
     serverless, porque a HostGator já roda PHP e assim não entra mais nenhum
     serviço na conta. O endpoint abaixo é nosso: api/inscrever.php.

     A chave do Brevo fica em rota-config.php, UM NÍVEL ACIMA da public_html —
     fora do alcance do navegador e fora do deploy. Enquanto esse arquivo não
     existir, o PHP responde 503 com {"configurar": true}, e este script cai
     no modo "cadastro manual por email". Continua sem fingir sucesso.

     Modelo do arquivo e instruções: api/rota-config.exemplo.php
     --------------------------------------------------------------------------- */
  var ESP_ENDPOINT = '/api/inscrever.php';

  /* ---------------------------------------------------------------------------
     ESP_MODO — como os dados viajam no POST. Dois valores possíveis:

       'form-data'  → envia como um formulário HTML normal (multipart/form-data).
                      É o que Brevo, Mailchimp e ConvertKit esperam nos endpoints
                      públicos de formulário. É o padrão porque é o mais
                      compatível: funciona sem "preflight" de CORS.

       'json'       → envia application/json no corpo. Use só se o endpoint for
                      seu (função serverless, API própria) e você souber que ele
                      lê JSON.

     Na dúvida, deixe 'form-data'.

     Aqui está 'json' porque o endpoint é o nosso api/inscrever.php, que lê
     JSON. Ele também aceita form-data, então trocar não quebra — mas não há
     motivo para trocar.
     --------------------------------------------------------------------------- */
  var ESP_MODO = 'json';

  /* ---------------------------------------------------------------------------
     GA4_ID — identificador de medição do Google Analytics 4, no formato
     G-XXXXXXXXXX.

     Onde achar: analytics.google.com → engrenagem "Administrador" (canto
     inferior esquerdo) → coluna "Propriedade" → "Fluxos de dados" → clique no
     fluxo do site rotacomfamilia.com.br → o campo "ID da métrica" (measurement ID)
     no topo direito. É esse valor, começando com "G-".

     Não confunda com:
       - "ID da propriedade" (só números, ex. 412345678) → não serve aqui.
       - GTM-XXXXXXX → isso é Google Tag Manager, outro produto.

     Se ficar vazio, nada do Google é carregado e os eventos viram console.debug
     (útil para testar no navegador sem sujar as estatísticas).
     --------------------------------------------------------------------------- */
  var GA4_ID = 'G-XVFFNMXYX3';

  /* ---------------------------------------------------------------------------
     ESP_CAMPOS — opcional. Nome que o SEU provedor dá para cada campo.
     Só mexa se o provedor reclamar de campo desconhecido.
       Brevo (padrão dos formulários):  { email: 'EMAIL',         nome: 'NOME'       }
       Mailchimp:                       { email: 'EMAIL',         nome: 'FNAME'      }
       ConvertKit/Kit:                  { email: 'email_address', nome: 'first_name' }
     --------------------------------------------------------------------------- */
  var ESP_CAMPOS = {
    email:  'email',
    nome:   'nome',
    origem: 'origem'
  };

  /* ###########################################################################
     ###              >>>  FIM DO BLOCO DE CONFIGURAÇÃO  <<<                 ###
     ###   Daqui para baixo é a mecânica. Não precisa editar para publicar.  ###
     ########################################################################### */


  /* ---------------------------------------------------------------------------
     Constantes da marca / do site
     --------------------------------------------------------------------------- */
  var EMAIL_CONTATO   = 'contato@rotacomfamilia.com.br';
  var PAGINA_PRIVACIDADE = 'privacidade.html';
  var CHAVE_CONSENTIMENTO = 'rcf_consentimento_v1'; // localStorage
  var NOME_HONEYPOT   = 'rcf_site_extra';           // campo isca antispam

  // Formulários que este arquivo controla. `#newsletter form` e
  // `form[data-waitlist]` estão aqui para assumir o lugar dos handlers antigos
  // mesmo que eles ainda existam no script.js / nos scripts inline das páginas.
  var SELETOR_FORMS = 'form[data-origem], form[data-waitlist], form[data-rota-form], #newsletter form';

  var MSG = {
    emailInvalido: 'Esse email não parece válido. Confira e tente de novo.',
    emailVazio:    'Escreva seu email para continuar.',
    enviando:      'Enviando…',
    sucesso:       'Pronto! Recebemos seu email. A confirmação chega em instantes. Se não aparecer, olhe a caixa de spam.',
    // O email vira um link clicável, por isso o texto termina aberto.
    erroRede:      'Não conseguimos enviar agora. Tente de novo ou escreva para ',
    // O envio pode ter chegado antes do tempo esgotar: pedimos para conferir
    // primeiro, senão a pessoa reenvia e o cadastro entra duplicado.
    erroTimeout:   'A resposta demorou demais. Confira seu email antes de tentar de novo, porque pode ser que já tenha dado certo. Se não chegou nada, escreva para ',
    // Redação condicional de propósito: em desktop sem cliente de email
    // configurado o mailto não abre nada, e afirmar que abriu seria mentira.
    fallback:      'Nosso cadastro automático ainda está sendo ligado, então esta inscrição é feita à mão. Se o seu programa de email não abriu sozinho:'
  };


  /* =============================================================================
     1. UTILITÁRIOS
     ============================================================================= */

  /** Executa fn quando o DOM estiver pronto (ou já agora, se estiver). */
  function aoCarregarDOM(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn, { once: true });
    } else {
      fn();
    }
  }

  /** O visitante pediu menos animação no sistema operacional? */
  function menosMovimento() {
    return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  /**
   * Validação de email do lado do cliente. Proposital: não é a regex "RFC
   * completa" (que aceita coisas que servidor nenhum entrega). É a checagem
   * pragmática — algo@algo.tld, sem espaços.
   */
  function emailValido(valor) {
    if (!valor) return false;
    var v = String(valor).trim();
    if (v.length > 254) return false;
    return /^[^\s@]+@[^\s@]+\.[A-Za-z]{2,}$/.test(v);
  }

  /** Nome curto da página atual: index.html → "home", cursos.html → "cursos". */
  function nomeDaPagina() {
    var arquivo = (window.location.pathname.split('/').pop() || 'index.html');
    arquivo = arquivo.replace(/\.[a-z]+$/i, '');
    if (!arquivo || arquivo === 'index') return 'home';
    return arquivo;
  }

  /** localStorage pode explodir (modo anônimo, storage bloqueado). Nunca deixe. */
  function lerStorage(chave) {
    try { return window.localStorage.getItem(chave); } catch (e) { return null; }
  }
  function gravarStorage(chave, valor) {
    try { window.localStorage.setItem(chave, valor); return true; } catch (e) { return false; }
  }


  /* =============================================================================
     2. CSS INJETADO
     Estilos mínimos das mensagens, do honeypot e do banner de cookies.
     Fica aqui para o HTML das páginas não precisar ser tocado.
     Paleta: deep #14150D · orange #D4A437 · cream #FAF1DA · flame #C8732E
     Fontes: só Inter (corpo) e Playfair Display (título) — as duas que ficam.
     ============================================================================= */
  function injetarCSS() {
    if (document.getElementById('rota-forms-css')) return;
    var css = [
      /* --- utilidade: esconder de verdade (Tailwind .grid/.flex vencem [hidden]) --- */
      '.rcf-oculto{display:none !important}',

      /* Nossos elementos não dependem do reset da página que nos hospeda. */
      '.rcf-cookies,.rcf-cookies *,.rcf-msg,.rcf-msg *{box-sizing:border-box}',

      /* --- honeypot: fora da tela, fora do tab, invisível para leitor de tela --- */
      '.rcf-hp{position:absolute !important;left:-10000px !important;top:auto !important;',
      'width:1px !important;height:1px !important;overflow:hidden !important;opacity:0 !important;pointer-events:none !important}',

      /* --- região de mensagem (sucesso / erro / fallback) --- */
      '.rcf-msg{display:none;margin-top:.75rem;padding:.85rem 1rem;border-radius:.85rem;',
      'font-family:"Inter",system-ui,-apple-system,"Segoe UI",sans-serif;font-size:.9rem;line-height:1.5;',
      'background:rgba(20,21,13,.94);border:1px solid rgba(212,164,55,.35);color:#FAF1DA;',
      'box-shadow:0 12px 32px -18px rgba(0,0,0,.8)}',
      '.rcf-msg.rcf-visivel{display:block}',
      '.rcf-msg:focus{outline:2px solid #D4A437;outline-offset:2px}',
      '.rcf-msg[data-tipo="erro"]{border-color:rgba(200,115,46,.75);color:#FAF1DA}',
      '.rcf-msg[data-tipo="sucesso"]{border-color:rgba(212,164,55,.75)}',
      '.rcf-msg a{color:#D4A437;text-decoration:underline;text-underline-offset:2px}',
      '.rcf-msg a:hover{color:#FAF1DA}',
      '.rcf-msg strong{color:#D4A437;font-weight:700}',

      /* --- campo com erro --- */
      '.rcf-campo-erro{border-color:#C8732E !important;box-shadow:0 0 0 2px rgba(200,115,46,.28) !important}',

      /* --- botão ocupado --- */
      'button[aria-busy="true"]{opacity:.72;cursor:progress}',

      /* ================= banner de cookies ================= */
      /* z-index 70: acima do header (z-50), abaixo dos modais (z-80). */
      '.rcf-cookies{position:fixed;z-index:70;left:1rem;right:1rem;bottom:1rem;max-width:34rem;margin-inline:auto;',
      'background:#14150D;border:1px solid rgba(212,164,55,.32);border-radius:1.1rem;padding:1.1rem 1.15rem;',
      'box-shadow:0 24px 60px -20px rgba(0,0,0,.85);color:#FAF1DA;',
      'font-family:"Inter",system-ui,-apple-system,"Segoe UI",sans-serif}',
      '@media (min-width:640px){.rcf-cookies{right:auto;left:1.25rem;bottom:1.25rem;margin-inline:0;max-width:26rem}}',
      '.rcf-cookies:focus{outline:2px solid #D4A437;outline-offset:3px}',
      '.rcf-cookies__titulo{font-family:"Playfair Display",Georgia,serif;font-size:1.05rem;font-weight:700;',
      'margin:0 0 .4rem;color:#FAF1DA;display:flex;align-items:center;gap:.5rem}',
      '.rcf-cookies__pin{width:.5rem;height:.5rem;border-radius:9999px;background:#D4A437;flex:0 0 auto}',
      '.rcf-cookies__texto{margin:0;font-size:.85rem;line-height:1.55;color:rgba(250,241,218,.78)}',
      '.rcf-cookies__acoes{display:flex;gap:.6rem;margin-top:.95rem;flex-wrap:wrap}',
      /* Aceitar e Recusar têm o MESMO tamanho, mesma fonte, mesmo peso.        */
      /* Recusar não é escondido, não é link pequeno, não é cinza apagado.      */
      '.rcf-cookies__btn{flex:1 1 8rem;min-height:2.6rem;padding:.6rem 1rem;border-radius:.7rem;',
      'font-family:inherit;font-size:.875rem;font-weight:700;line-height:1;cursor:pointer;',
      'transition:background .18s ease,color .18s ease,border-color .18s ease}',
      '.rcf-cookies__btn--sim{background:#D4A437;color:#14150D;border:1px solid #D4A437}',
      '.rcf-cookies__btn--sim:hover{background:#E3B04B;border-color:#E3B04B}',
      '.rcf-cookies__btn--nao{background:transparent;color:#FAF1DA;border:1px solid rgba(250,241,218,.45)}',
      '.rcf-cookies__btn--nao:hover{background:rgba(250,241,218,.12);border-color:#FAF1DA}',
      '.rcf-cookies__btn:focus-visible{outline:2px solid #FAF1DA;outline-offset:2px}',
      '.rcf-cookies__btn--sim:focus-visible{outline-color:#FAF1DA}',
      '.rcf-cookies__link{display:inline-block;margin-top:.7rem;font-size:.78rem;color:rgba(250,241,218,.62);',
      'text-decoration:underline;text-underline-offset:2px}',
      '.rcf-cookies__link:hover{color:#D4A437}',
      '.rcf-cookies__link:focus-visible{outline:2px solid #D4A437;outline-offset:2px;border-radius:.2rem}',
      /* animação de entrada, desligada para quem pede menos movimento */
      '@media (prefers-reduced-motion:no-preference){',
      '.rcf-cookies{animation:rcf-sobe .38s cubic-bezier(.2,.7,.3,1) both}',
      '@keyframes rcf-sobe{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}}',
      '@media (prefers-reduced-motion:reduce){.rcf-cookies{animation:none}}',

      /* ================= botão flutuante de WhatsApp ================= */
      /* Canto inferior direito. No desktop o banner de cookies fica embaixo à
         esquerda, então não se encostam; no celular o banner ocupa a largura
         toda, e por isso o botão só entra depois que o visitante responde. */
      '.rcf-zap{position:fixed;z-index:60;right:1rem;bottom:1rem;display:inline-flex;align-items:center;',
      'gap:.55rem;height:3.5rem;padding:0 1.05rem;border-radius:9999px;text-decoration:none;',
      'background:linear-gradient(135deg,#D4A437,#C8732E);color:#14150D;font-family:Inter,system-ui,sans-serif;',
      'font-weight:700;font-size:.95rem;line-height:1;box-shadow:0 10px 30px -8px rgba(0,0,0,.55);',
      'border:1px solid rgba(250,241,218,.22)}',
      '@media (min-width:640px){.rcf-zap{right:1.25rem;bottom:1.25rem}}',
      '.rcf-zap:hover{background:linear-gradient(135deg,#E3B04B,#D4832E)}',
      '.rcf-zap:focus-visible{outline:3px solid #FAF1DA;outline-offset:3px}',
      '.rcf-zap svg{width:1.6rem;height:1.6rem;flex:0 0 auto;fill:currentColor}',
      /* O rótulo fica escondido enquanto o botão está em repouso: no telefone
         ele roubaria metade da tela. Aparece no hover e no foco por teclado. */
      '.rcf-zap__txt{max-width:0;overflow:hidden;white-space:nowrap;opacity:0}',
      '@media (prefers-reduced-motion:no-preference){',
      '.rcf-zap{transition:background .25s ease,transform .25s ease}',
      '.rcf-zap:hover{transform:translateY(-2px)}',
      '.rcf-zap__txt{transition:max-width .28s cubic-bezier(.2,.7,.3,1),opacity .2s ease}}',
      '.rcf-zap:hover .rcf-zap__txt,.rcf-zap:focus-visible .rcf-zap__txt{max-width:11rem;opacity:1}',
      /* Em repouso o botão é só o ícone, e aí precisa ficar redondo. Além do
         padding, o gap tem de zerar: ele continua ocupando espaço entre o ícone
         e um rótulo de largura zero, e sobrava um botão oval de 67 por 56. */
      '.rcf-zap:not(:hover):not(:focus-visible){gap:0;padding-left:.95rem;padding-right:.95rem}',
      '@media (prefers-reduced-motion:no-preference){',
      '.rcf-zap{animation:rcf-zap-entra .32s cubic-bezier(.2,.7,.3,1) both}',
      '@keyframes rcf-zap-entra{from{opacity:0;transform:scale(.85)}to{opacity:1;transform:none}}}',
      /* Em tela muito baixa (celular deitado) o botão atrapalha mais que ajuda */
      '@media (max-height:26rem){.rcf-zap{display:none}}'
    ].join('');

    var tag = document.createElement('style');
    tag.id = 'rota-forms-css';
    tag.textContent = css;
    (document.head || document.documentElement).appendChild(tag);
  }


  /* =============================================================================
     3. ANALYTICS (GA4 via gtag) — carregado SÓ depois do aceite
     ============================================================================= */
  var GA = (function () {
    var carregado = false;

    /** Injeta o gtag.js. Chamado exclusivamente após consentimento = 'aceito'. */
    function carregar() {
      if (carregado || !GA4_ID) return;
      carregado = true;

      window.dataLayer = window.dataLayer || [];
      // gtag precisa ser uma function tradicional (usa `arguments`).
      window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
      window.gtag('js', new Date());
      window.gtag('config', GA4_ID, {
        // O GA4 já anonimiza o IP por padrão; anonymize_ip era parâmetro do
        // Universal Analytics e é ignorado aqui, então não vale declarar.
        send_page_view: true
      });

      var s = document.createElement('script');
      s.async = true;
      s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA4_ID);
      (document.head || document.documentElement).appendChild(s);
    }

    /** Dispara um evento. Sem GA4_ID ou sem consentimento, vira log de debug. */
    function evento(nome, parametros) {
      var params = parametros || {};
      params.pagina = params.pagina || nomeDaPagina();

      if (!GA4_ID) {
        console.debug('[Rota][evento, GA4 não configurado]', nome, params);
        return;
      }
      if (Consentimento.ler() !== 'aceito') {
        console.debug('[Rota][evento, sem consentimento]', nome, params);
        return;
      }
      if (typeof window.gtag !== 'function') {
        console.debug('[Rota][evento, gtag ainda não carregou]', nome, params);
        return;
      }
      window.gtag('event', nome, params);
    }

    return { carregar: carregar, evento: evento };
  })();


  /* =============================================================================
     4. CONSENTIMENTO + BANNER DE COOKIES
     ============================================================================= */
  var Consentimento = (function () {

    function ler() {
      var v = lerStorage(CHAVE_CONSENTIMENTO);
      return (v === 'aceito' || v === 'recusado') ? v : null;
    }

    function gravar(valor) {
      gravarStorage(CHAVE_CONSENTIMENTO, valor);
      // Avisa quem estiver esperando a decisão (hoje, o botão flutuante).
      // Evento em vez de callback para não criar ordem de carregamento entre
      // os módulos deste arquivo.
      try {
        document.dispatchEvent(new CustomEvent('rcf:consentimento', {
          detail: { escolha: valor }
        }));
      } catch (e) {
        // navegador antigo sem CustomEvent: o botão entra no próximo carregamento
      }
    }

    /** Remove o banner da tela (com fade curto, se o visitante aceitar animação). */
    function fechar(banner, focoDeVolta) {
      if (!banner) return;
      var remover = function () {
        if (banner.parentNode) banner.parentNode.removeChild(banner);
        if (focoDeVolta && typeof focoDeVolta.focus === 'function') {
          try { focoDeVolta.focus(); } catch (e) { /* ignora */ }
        }
      };
      if (menosMovimento()) {
        remover();
      } else {
        banner.style.transition = 'opacity .22s ease, transform .22s ease';
        banner.style.opacity = '0';
        banner.style.transform = 'translateY(10px)';
        window.setTimeout(remover, 230);
      }
    }

    /**
     * Monta o banner. Não é modal: não prende o foco nem bloqueia a página.
     * Mas recebe o foco ao aparecer, para quem navega por teclado não precisar
     * varrer a página inteira até achá-lo.
     */
    function mostrarBanner() {
      if (document.querySelector('.rcf-cookies')) return; // já está na tela

      var focoAnterior = document.activeElement;

      var banner = document.createElement('section');
      banner.className = 'rcf-cookies';
      banner.setAttribute('role', 'region');
      banner.setAttribute('aria-label', 'Aviso de cookies e privacidade');
      banner.setAttribute('tabindex', '-1');

      var titulo = document.createElement('h2');
      titulo.className = 'rcf-cookies__titulo';
      var pin = document.createElement('span');
      pin.className = 'rcf-cookies__pin';
      pin.setAttribute('aria-hidden', 'true');
      titulo.appendChild(pin);
      titulo.appendChild(document.createTextNode('Cookies e privacidade'));

      var texto = document.createElement('p');
      texto.className = 'rcf-cookies__texto';
      texto.textContent = 'Usamos medição de audiência (Google Analytics) só para saber quais conteúdos ajudam mais famílias a viajar. Nada é carregado antes de você decidir.';

      var acoes = document.createElement('div');
      acoes.className = 'rcf-cookies__acoes';

      var btnSim = document.createElement('button');
      btnSim.type = 'button';
      btnSim.className = 'rcf-cookies__btn rcf-cookies__btn--sim';
      btnSim.textContent = 'Aceitar';

      var btnNao = document.createElement('button');
      btnNao.type = 'button';
      btnNao.className = 'rcf-cookies__btn rcf-cookies__btn--nao';
      btnNao.textContent = 'Recusar';

      // Ordem no DOM: Aceitar, Recusar. Mesmo tamanho, mesmo destaque tipográfico.
      acoes.appendChild(btnSim);
      acoes.appendChild(btnNao);

      var link = document.createElement('a');
      link.className = 'rcf-cookies__link';
      link.href = PAGINA_PRIVACIDADE;
      link.textContent = 'Ler a política de privacidade';

      banner.appendChild(titulo);
      banner.appendChild(texto);
      banner.appendChild(acoes);
      banner.appendChild(link);

      btnSim.addEventListener('click', function () {
        gravar('aceito');
        fechar(banner, focoAnterior);
        GA.carregar();
        // Primeiro evento só depois do aceite — nunca antes.
        window.setTimeout(function () { GA.evento('consentimento_aceito', {}); }, 60);
      });

      btnNao.addEventListener('click', function () {
        gravar('recusado');
        fechar(banner, focoAnterior);
        console.debug('[Rota] Consentimento recusado: Google Analytics não será carregado.');
      });

      document.body.appendChild(banner);

      // Leva o foco para o banner (sem rolar a página).
      window.setTimeout(function () {
        try { banner.focus({ preventScroll: true }); } catch (e) { banner.focus(); }
      }, 120);
    }

    /** Estado inicial: já escolheu? aplica. Nunca escolheu? mostra o banner. */
    function iniciar() {
      var escolha = ler();

      if (escolha === 'aceito') {
        GA.carregar();
        return;
      }
      if (escolha === 'recusado') {
        return; // nada de Google, nunca.
      }
      mostrarBanner();
    }

    /** Permite um link "gerenciar cookies" em qualquer página. */
    function reabrir() {
      try { window.localStorage.removeItem(CHAVE_CONSENTIMENTO); } catch (e) { /* ignora */ }
      mostrarBanner();
    }

    return { ler: ler, iniciar: iniciar, mostrarBanner: mostrarBanner, reabrir: reabrir };
  })();


  /* =============================================================================
     4b. BOTÃO FLUTUANTE DE WHATSAPP
     ============================================================================= */

  /* O número vive aqui, em um lugar só. Se mudar de novo, é esta linha. Os
     botões escritos no HTML das páginas continuam existindo; este é o atalho
     que acompanha a rolagem. */
  var ZAP_NUMERO = '5541988652343';

  /* Texto neutro de propósito. Quem clica aqui pode estar querendo falar de uma
     viagem, de parceria ou de emissão, e não dá para saber qual. Uma mensagem
     pronta do tipo "quero contratar" põe palavra na boca de quem só tinha uma
     dúvida. */
  var ZAP_TEXTO = 'Oi! Vim pelo site da Rota com Família.';

  function montarBotaoZap() {
    if (document.querySelector('.rcf-zap')) return;

    var a = document.createElement('a');
    a.className = 'rcf-zap';
    a.href = 'https://wa.me/' + ZAP_NUMERO + '?text=' + encodeURIComponent(ZAP_TEXTO);
    a.target = '_blank';
    a.rel = 'noopener';
    // O rótulo visível só aparece no hover, então o nome acessível vem daqui.
    a.setAttribute('aria-label', 'Falar com a Rota com Família no WhatsApp');
    /* Quem dispara o evento do GA4 é o handler delegado no fim deste arquivo,
       que já escuta qualquer link de wa.me e respeita data-origem. Registrar um
       listener próprio aqui contava o mesmo clique duas vezes. */
    a.setAttribute('data-origem', 'flutuante');

    a.innerHTML =
      '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
      '<path d="M17.5 14.4c-.3-.2-1.7-.9-2-1-.3-.1-.5-.2-.7.2s-.8 1-1 1.2c-.2.2-.4.2-.7 0' +
      '-.3-.2-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6.1-.1.3-.4.4-.6.1-.2.2-.3.3-.5' +
      '.1-.2 0-.4 0-.5-.1-.2-.7-1.7-1-2.3-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.4' +
      '0 1.4 1 2.8 1.2 3 .1.2 2 3.1 4.9 4.3.7.3 1.2.5 1.6.6.7.2 1.3.2 1.8.1.6-.1 1.7-.7 1.9-1.4' +
      '.2-.7.2-1.2.2-1.4 0-.2-.3-.2-.6-.4zM12 2C6.5 2 2 6.5 2 12c0 1.8.5 3.5 1.3 4.9L2 22l5.3-1.3' +
      'c1.3.7 2.9 1.1 4.6 1.1 5.5 0 10-4.5 10-10S17.5 2 12 2z"/></svg>' +
      '<span class="rcf-zap__txt">Falar no WhatsApp</span>';

    document.body.appendChild(a);
  }

  /* No celular o banner de cookies ocupa a largura toda embaixo e cobriria o
     botão. Em vez de empurrar o botão para o meio da tela, ele espera: o banner
     é a decisão mais importante da primeira visita, e aparece uma única vez.

     A primeira versão disto ficava consultando o localStorage a cada 400 ms,
     com um limite de 12 segundos para não girar para sempre. Estava errado: se
     a pessoa deixasse o banner na tela por mais de 12 segundos, o que é
     absolutamente normal, o limite cancelava o vigia e o botão nunca mais
     aparecia naquela visita. Agora quem grava a escolha é que avisa. */
  function iniciarBotaoZap() {
    if (Consentimento.ler() !== null) {
      montarBotaoZap();
      return;
    }
    document.addEventListener('rcf:consentimento', function () {
      montarBotaoZap();
    }, { once: true });
  }


  /* =============================================================================
     4c. COPIAR CUPOM
     ============================================================================= */

  /* Digitar 2R3N9APMTM no teclado do celular erra na primeira tentativa. O
     botão só entra quando o navegador tem a API de área de transferência: sem
     ela, o código continua na tela para selecionar com o dedo, que é o
     comportamento de antes. */
  function ligarCopiarCupom() {
    if (!navigator.clipboard || !navigator.clipboard.writeText) return;

    var codigos = document.querySelectorAll('[data-copiar]');
    Array.prototype.forEach.call(codigos, function (code) {
      if (code.nextElementSibling &&
          code.nextElementSibling.classList.contains('parceria-copiar')) return;

      var texto = code.getAttribute('data-copiar') || code.textContent.trim();
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'parceria-copiar';
      btn.textContent = 'Copiar';
      btn.setAttribute('aria-label', 'Copiar o cupom ' + texto);

      btn.addEventListener('click', function () {
        navigator.clipboard.writeText(texto).then(function () {
          btn.textContent = 'Copiado';
          btn.setAttribute('data-copiado', '1');
          GA.evento('copiar_cupom', { cupom: texto, pagina: nomeDaPagina() });
          window.setTimeout(function () {
            btn.textContent = 'Copiar';
            btn.removeAttribute('data-copiado');
          }, 2200);
        })['catch'](function () {
          // Alguns navegadores negam a área de transferência sem gesto direto
          // ou fora de HTTPS. Em vez de falhar calado, seleciona o código para
          // a pessoa copiar com o atalho do teclado.
          btn.textContent = 'Selecione e copie';
          try {
            var faixa = document.createRange();
            faixa.selectNodeContents(code);
            var sel = window.getSelection();
            sel.removeAllRanges();
            sel.addRange(faixa);
          } catch (e) { /* ignora */ }
        });
      });

      code.parentNode.insertBefore(btn, code.nextSibling);
    });
  }


  /* =============================================================================
     5. FORMULÁRIOS — captura de email honesta
     ============================================================================= */
  var contadorMsg = 0;

  /** Descobre de onde veio o lead. data-origem manda; o resto é palpite útil. */
  function origemDoForm(form) {
    if (form.getAttribute('data-origem')) return form.getAttribute('data-origem');
    if (form.getAttribute('data-waitlist')) return 'lista-espera-' + form.getAttribute('data-waitlist');
    if (form.closest('#newsletter')) return 'newsletter-' + nomeDaPagina();
    var secao = form.closest('section[id]');
    if (secao) return secao.id + '-' + nomeDaPagina();
    return 'form-' + nomeDaPagina();
  }

  function botaoDoForm(form) {
    return form.querySelector('button[type="submit"], input[type="submit"], button');
  }

  function campoEmail(form) {
    return form.querySelector('input[type="email"]') ||
           form.querySelector('input[name="email"], input[name="EMAIL"]');
  }

  function campoNome(form) {
    return form.querySelector('input[data-campo="nome"], input[name="nome"], input[name="FNAME"]') ||
           form.querySelector('input[type="text"]:not([data-rcf-hp])');
  }

  /**
   * Honeypot: um campo que só robô preenche. Fica fora da tela, fora da ordem
   * de tabulação e escondido de leitores de tela. Se vier preenchido, fingimos
   * sucesso (para o robô não tentar de novo) e não enviamos nada.
   */
  function garantirHoneypot(form) {
    if (form.querySelector('[data-rcf-hp]')) return;
    var caixa = document.createElement('div');
    caixa.className = 'rcf-hp';
    caixa.setAttribute('aria-hidden', 'true');

    var input = document.createElement('input');
    input.type = 'text';
    input.name = NOME_HONEYPOT;
    input.tabIndex = -1;
    input.autocomplete = 'off';
    input.setAttribute('data-rcf-hp', '');
    input.setAttribute('aria-hidden', 'true');
    // Opt-outs dos gerenciadores de senha. Sem isto, o 1Password ou o LastPass
    // podem preencher a isca sozinhos e uma pessoa real cairia no ramo do
    // honeypot: veria "sucesso" e o lead seria descartado em silêncio.
    input.setAttribute('data-lpignore', 'true');
    input.setAttribute('data-1p-ignore', '');
    input.setAttribute('data-form-type', 'other');

    caixa.appendChild(input);
    form.appendChild(caixa);
  }

  /** Cria (uma vez) a região aria-live logo depois do formulário. */
  function garantirMensagem(form) {
    var existente = form.nextElementSibling;
    if (existente && existente.classList && existente.classList.contains('rcf-msg')) return existente;

    contadorMsg += 1;
    var msg = document.createElement('div');
    msg.className = 'rcf-msg';
    msg.id = 'rcf-msg-' + contadorMsg;
    msg.setAttribute('role', 'status');
    msg.setAttribute('aria-live', 'polite');
    msg.setAttribute('tabindex', '-1');

    if (form.parentNode) form.parentNode.insertBefore(msg, form.nextSibling);
    return msg;
  }

  /**
   * Escreve na região de mensagem.
   * @param {string} tipo  'sucesso' | 'erro' | 'aviso'
   * @param {Node[]|string} conteudo  texto ou nós já montados
   * @param {boolean} focar  leva o foco para a mensagem
   */
  function mostrarMensagem(form, tipo, conteudo, focar) {
    var msg = garantirMensagem(form);
    msg.setAttribute('data-tipo', tipo);
    msg.textContent = '';

    if (typeof conteudo === 'string') {
      msg.appendChild(document.createTextNode(conteudo));
    } else if (Array.isArray(conteudo)) {
      conteudo.forEach(function (n) { msg.appendChild(n); });
    } else if (conteudo) {
      msg.appendChild(conteudo);
    }

    msg.classList.add('rcf-visivel');
    if (focar) {
      try { msg.focus({ preventScroll: false }); } catch (e) { msg.focus(); }
    }
    return msg;
  }

  function limparMensagem(form) {
    var msg = form.nextElementSibling;
    if (msg && msg.classList && msg.classList.contains('rcf-msg')) {
      msg.classList.remove('rcf-visivel');
      msg.textContent = '';
      msg.removeAttribute('data-tipo');
    }
  }

  function botaoOcupado(btn, ocupado, textoOcupado) {
    if (!btn) return;
    if (ocupado) {
      // Guardamos innerHTML, não textContent: vários botões do site trazem um
      // <svg> dentro, e usar texto puro destruiria o ícone na restauração.
      // O conteúdo é sempre do próprio site, nunca entrada de usuário.
      if (btn.getAttribute('data-rcf-html') === null) {
        btn.setAttribute('data-rcf-html', btn.innerHTML);
      }
      btn.setAttribute('aria-busy', 'true');
      btn.disabled = true;
      btn.textContent = textoOcupado || MSG.enviando;
    } else {
      btn.removeAttribute('aria-busy');
      btn.disabled = false;
      var original = btn.getAttribute('data-rcf-html');
      if (original !== null) {
        btn.innerHTML = original;
        btn.removeAttribute('data-rcf-html');
      }
    }
  }

  /** Marca/desmarca o campo de email como inválido, ligado à mensagem por aria. */
  function marcarErroCampo(input, msgEl) {
    if (!input) return;
    input.setAttribute('aria-invalid', 'true');
    input.classList.add('rcf-campo-erro');
    if (msgEl && msgEl.id) input.setAttribute('aria-describedby', msgEl.id);
  }
  function limparErroCampo(input) {
    if (!input) return;
    input.removeAttribute('aria-invalid');
    // Sem remover isto, o leitor de tela continua anunciando a descrição do
    // erro antigo mesmo depois do campo ter sido corrigido.
    input.removeAttribute('aria-describedby');
    input.classList.remove('rcf-campo-erro');
  }

  /** Monta o corpo do POST conforme ESP_MODO. */
  function montarEnvio(dados) {
    if (ESP_MODO === 'json') {
      var corpo = {};
      corpo[ESP_CAMPOS.email]  = dados.email;
      if (dados.nome) corpo[ESP_CAMPOS.nome] = dados.nome;
      corpo[ESP_CAMPOS.origem] = dados.origem;
      corpo.pagina    = dados.pagina;
      corpo.url       = dados.url;
      corpo.enviado_em = dados.enviado_em;
      return {
        body: JSON.stringify(corpo),
        headers: { 'Content-Type': 'application/json' }
      };
    }

    // 'form-data' (padrão): sem header de Content-Type — o navegador escreve o
    // boundary sozinho. Setar na mão quebra o multipart.
    var fd = new FormData();
    fd.append(ESP_CAMPOS.email, dados.email);
    if (dados.nome) fd.append(ESP_CAMPOS.nome, dados.nome);
    fd.append(ESP_CAMPOS.origem, dados.origem);
    fd.append('pagina', dados.pagina);
    fd.append('url', dados.url);
    fd.append('enviado_em', dados.enviado_em);
    return { body: fd, headers: undefined };
  }

  /** Sucesso de verdade: esconde o form, mostra a mensagem, dispara o evento. */
  function concluirComSucesso(form, dados, textoCustom) {
    form.reset();
    form.setAttribute('hidden', '');
    form.classList.add('rcf-oculto');

    var texto = textoCustom || form.getAttribute('data-msg-sucesso') || MSG.sucesso;
    mostrarMensagem(form, 'sucesso', texto, true);

    GA.evento('lead_enviado', { origem: dados.origem, metodo: 'esp' });
  }

  /**
   * Modo sem ESP configurado. Não fingimos sucesso: abrimos um email pronto
   * para a pessoa enviar, e dizemos com todas as letras que o cadastro é manual.
   */
  function fallbackMailto(form, dados) {
    console.warn(
      '[Rota com Família] ESP_ENDPOINT está vazio em assets/rota-forms.js. ' +
      'nenhum lead está sendo enviado automaticamente. O formulário caiu no modo ' +
      'mailto (cadastro manual). Preencha ESP_ENDPOINT no bloco de configuração ' +
      'do arquivo para ligar o envio de verdade.'
    );

    var assunto = 'Quero entrar na lista: ' + dados.origem;
    var corpo =
      'Olá, Jefferson e Kharol!\n\n' +
      'Quero entrar na lista de emails do Rota com Família.\n\n' +
      'Nome: ' + (dados.nome || '(não informado)') + '\n' +
      'Email: ' + dados.email + '\n' +
      'Origem: ' + dados.origem + '\n' +
      'Página: ' + dados.url + '\n\n' +
      '(Mensagem gerada pelo formulário do site.)';

    var href = 'mailto:' + EMAIL_CONTATO +
               '?subject=' + encodeURIComponent(assunto) +
               '&body=' + encodeURIComponent(corpo);

    // O formulário CONTINUA visível de propósito. Em desktop sem cliente de
    // email configurado (quem usa Gmail no navegador, por exemplo) o mailto
    // não abre nada: se escondêssemos o formulário, a pessoa perderia o que
    // digitou e ficaria sem saída.
    var frase = document.createElement('span');
    frase.textContent = MSG.fallback + ' ';

    var link = document.createElement('a');
    link.href = href;
    link.textContent = 'Enviar por email';

    var ou = document.createElement('span');
    ou.textContent = ' ou escreva para ' + EMAIL_CONTATO + '.';

    mostrarMensagem(form, 'aviso', [frase, link, ou], true);

    // Tenta abrir o cliente de email (estamos dentro de um gesto do usuário).
    try { window.location.href = href; } catch (e) { /* o link acima resolve */ }

    // Evento propositalmente DIFERENTE de `lead_enviado`: aqui nada foi enviado
    // ao provedor, só abrimos um email. Contar isso como lead capturado seria
    // mentir de novo — agora no relatório.
    GA.evento('lead_fallback_mailto', { origem: dados.origem });
  }

  /**
   * Alguns provedores respondem HTTP 200 com um corpo dizendo que deu errado
   * (o Mailchimp devolve {"result":"error"} com status 200, por exemplo).
   * Confiar só no status seria recriar o falso sucesso que este arquivo existe
   * para eliminar, então quando a resposta for JSON nós lemos o corpo.
   * Resposta que não for JSON continua sendo avaliada pelo status HTTP.
   */
  function conferirCorpo(resp) {
    var tipo = (resp.headers && resp.headers.get('content-type')) || '';
    if (tipo.indexOf('json') === -1) return resp;

    return resp.clone().json().then(function (dados) {
      if (!dados || typeof dados !== 'object') return resp;

      var resultado = String(dados.result || dados.status || '').toLowerCase();
      var temErro = resultado === 'error' || resultado === 'fail' ||
                    dados.error || dados.errors ||
                    (dados.code && dados.code >= 400);

      if (temErro) {
        var motivo = dados.msg || dados.message || dados.error || resultado || 'erro do provedor';
        throw new Error('provedor recusou: ' + String(motivo).slice(0, 200));
      }
      return resp;
    }, function () {
      // Corpo anunciado como JSON mas ilegível: não temos como afirmar que
      // falhou, então mantemos o veredito do status HTTP.
      return resp;
    });
  }

  /** Envio real por fetch. */
  function enviarParaESP(form, dados, btn, inputEmail) {
    botaoOcupado(btn, true);
    limparMensagem(form);

    var abortou = false;
    var idTimeout = null;

    /** Mensagem honesta de falha, reaproveitada pelos dois caminhos de erro. */
    function falhar(erro, textoBase) {
      if (idTimeout) window.clearTimeout(idTimeout);
      botaoOcupado(btn, false);
      console.error('[Rota] Falha ao enviar o lead:', erro);

      var texto = document.createElement('span');
      texto.textContent = textoBase || MSG.erroRede;

      var link = document.createElement('a');
      link.href = 'mailto:' + EMAIL_CONTATO;
      link.textContent = EMAIL_CONTATO;

      var ponto = document.createTextNode('.');

      // NÃO limpamos o campo e NÃO escondemos o formulário: a pessoa não pode
      // perder o que digitou nem ficar sem meio de tentar de novo.
      mostrarMensagem(form, 'erro', [texto, link, ponto], true);
      GA.evento('lead_erro', { origem: dados.origem });
    }

    var requisicao;
    try {
      var envio = montarEnvio(dados);
      var opcoes = {
        method: 'POST',
        body: envio.body,
        // 'omit' evita mandar cookies de terceiros junto do lead.
        credentials: 'omit'
      };
      if (envio.headers) opcoes.headers = envio.headers;

      // Rede lenta não pode deixar o botão travado para sempre.
      var controller = ('AbortController' in window) ? new AbortController() : null;
      if (controller) {
        opcoes.signal = controller.signal;
        idTimeout = window.setTimeout(function () {
          abortou = true;
          controller.abort();
        }, 15000);
      }

      requisicao = fetch(ESP_ENDPOINT, opcoes);
    } catch (erroSincrono) {
      // FormData/fetch ausentes, URL malformada: sem este try o botão ficaria
      // travado em "Enviando…" para sempre, sem mensagem nenhuma.
      falhar(erroSincrono);
      return;
    }

    // Sentinela para o caso "servidor no ar, mas Brevo ainda não configurado".
    var NAO_CONFIGURADO = { rcfNaoConfigurado: true };

    requisicao
      .then(function (resp) {
        // 503 com {"configurar": true} vem do nosso api/inscrever.php quando o
        // rota-config.php ainda não existe no servidor, ou quando a chave do
        // Brevo foi recusada. Não é falha de rede nem erro da pessoa, então não
        // mostramos mensagem de erro: caímos no mesmo modo de cadastro manual
        // usado quando não há endpoint nenhum.
        if (resp.status === 503) {
          return resp.json()
            .catch(function () { return null; })
            .then(function (corpo) {
              if (corpo && corpo.configurar) return NAO_CONFIGURADO;
              throw new Error('HTTP 503');
            });
        }
        if (!resp.ok) throw new Error('HTTP ' + resp.status);
        return conferirCorpo(resp);
      })
      .then(function (resultado) {
        if (idTimeout) window.clearTimeout(idTimeout);
        botaoOcupado(btn, false);

        if (resultado === NAO_CONFIGURADO) {
          console.warn(
            '[Rota] api/inscrever.php respondeu que o Brevo não está configurado. ' +
            'Crie o rota-config.php um nível acima da public_html ' +
            '(modelo em api/rota-config.exemplo.php). Usando cadastro manual por email.'
          );
          fallbackMailto(form, dados);
          return;
        }

        limparErroCampo(inputEmail);
        concluirComSucesso(form, dados);
      })
      .catch(function (erro) {
        // Tempo esgotado é ambíguo: o servidor pode ter processado o cadastro
        // antes do abort. Pedir para conferir o email evita cadastro duplicado.
        falhar(
          abortou ? 'tempo esgotado' : erro,
          abortou ? MSG.erroTimeout : null
        );
      });
  }

  /** Handler único de submit. */
  function tratarSubmit(form) {
    garantirHoneypot(form);

    var origem     = origemDoForm(form);
    var btn        = botaoDoForm(form);
    var inputEmail = campoEmail(form);
    var inputNome  = campoNome(form);
    var isca       = form.querySelector('[data-rcf-hp]');

    // --- Honeypot preenchido: é robô. Fingimos sucesso e não enviamos nada. ---
    if (isca && isca.value.trim() !== '') {
      console.debug('[Rota] Honeypot preenchido: envio descartado (provável bot).');
      form.reset();
      form.setAttribute('hidden', '');
      form.classList.add('rcf-oculto');
      mostrarMensagem(form, 'sucesso', MSG.sucesso, false);
      return;
    }

    // --- Validação de email (mensagem acessível, nunca alert()) ---
    var valorEmail = inputEmail ? inputEmail.value.trim() : '';
    if (!valorEmail) {
      var m1 = mostrarMensagem(form, 'erro', MSG.emailVazio, true);
      marcarErroCampo(inputEmail, m1);
      if (inputEmail) inputEmail.focus();
      return;
    }
    if (!emailValido(valorEmail)) {
      var m2 = mostrarMensagem(form, 'erro', MSG.emailInvalido, true);
      marcarErroCampo(inputEmail, m2);
      return;
    }
    limparErroCampo(inputEmail);
    limparMensagem(form);

    var dados = {
      email:      valorEmail,
      nome:       inputNome ? inputNome.value.trim() : '',
      origem:     origem,
      pagina:     nomeDaPagina(),
      url:        window.location.href,
      enviado_em: new Date().toISOString()
    };

    if (ESP_ENDPOINT) {
      enviarParaESP(form, dados, btn, inputEmail);
    } else {
      fallbackMailto(form, dados);
    }
  }

  /**
   * Captura o submit na fase de CAPTURA, no document.
   *
   * Por que assim: os handlers antigos (script.js e os <script> inline de
   * cursos.html / ebooks.html) estão presos ao próprio <form>. Um listener de
   * captura no document roda ANTES deles; com stopImmediatePropagation o evento
   * nunca chega lá. Funciona mesmo que os handlers antigos continuem no lugar e
   * independe da ordem de carregamento dos scripts.
   *
   * Por que NÃO clonamos o <form> para descartar listeners: os formulários têm
   * a classe .reveal, observada pelo IntersectionObserver do script.js. Um clone
   * não estaria sendo observado e o formulário ficaria invisível para sempre.
   */
  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form || form.nodeType !== 1 || form.tagName !== 'FORM') return;
    if (typeof form.matches !== 'function' || !form.matches(SELETOR_FORMS)) return;

    e.preventDefault();
    e.stopImmediatePropagation();   // silencia os handlers antigos
    tratarSubmit(form);
  }, true);


  /* =============================================================================
     6. EVENTOS DE ANALYTICS POR DELEGAÇÃO
     Um único listener no document cobre todas as páginas. Nenhum link precisa
     ser marcado à mão — data-origem é opcional e só refina o relatório.
     ============================================================================= */

  function nomeDoArquivo(href) {
    try {
      var u = new URL(href, window.location.href);
      return decodeURIComponent(u.pathname.split('/').pop() || href);
    } catch (e) {
      return href.split('/').pop() || href;
    }
  }

  function redeSocial(href) {
    var h = href.toLowerCase();
    if (h.indexOf('youtube.com') > -1 || h.indexOf('youtu.be') > -1) return 'youtube';
    if (h.indexOf('instagram.com') > -1) return 'instagram';
    if (h.indexOf('tiktok.com') > -1) return 'tiktok';
    return null;
  }

  document.addEventListener('click', function (e) {
    var alvo = e.target;
    if (!alvo || typeof alvo.closest !== 'function') return;

    // Link "gerenciar cookies" em qualquer página (ex.: privacidade.html).
    var gerenciar = alvo.closest('[data-abrir-cookies]');
    if (gerenciar) {
      e.preventDefault();
      Consentimento.reabrir();
      return;
    }

    var a = alvo.closest('a[href]');
    if (!a) return;

    var href = a.getAttribute('href') || '';
    var origem = a.getAttribute('data-origem') || nomeDaPagina();

    // --- WhatsApp ---
    if (href.indexOf('wa.me') > -1 || href.indexOf('api.whatsapp.com') > -1) {
      // origem diz de que ponto da página saiu o clique; pagina diz de qual
      // página. O botão flutuante existe nas sete, então os dois importam.
      GA.evento('clique_whatsapp', { origem: origem, pagina: nomeDaPagina() });
      return;
    }

    // --- Link de parceiro (página de parcerias) ---
    var parceiro = a.getAttribute('data-parceiro');
    if (parceiro) {
      GA.evento('clique_parceiro', { parceiro: parceiro, pagina: nomeDaPagina() });
      return;
    }

    // --- Download de ebook / PDF ---
    var ehPdf = /\.pdf(\?|#|$)/i.test(href);
    if (a.hasAttribute('download') || ehPdf) {
      GA.evento('download_ebook', {
        arquivo: nomeDoArquivo(href),
        origem: origem
      });
      return;
    }

    // --- Redes sociais ---
    var rede = redeSocial(href);
    if (rede) {
      GA.evento('clique_social', { rede: rede, origem: origem });
    }
  }, false);


  /* =============================================================================
     7. INICIALIZAÇÃO
     ============================================================================= */
  injetarCSS();

  aoCarregarDOM(function () {
    // Honeypot + região de mensagem já prontos antes do primeiro submit.
    var forms = document.querySelectorAll(SELETOR_FORMS);
    Array.prototype.forEach.call(forms, function (form) {
      garantirHoneypot(form);
      garantirMensagem(form);
      form.setAttribute('novalidate', '');  // a validação/mensagem é nossa, acessível
    });

    if (!ESP_ENDPOINT && forms.length) {
      console.warn(
        '[Rota com Família] ' + forms.length + ' formulário(s) nesta página estão em ' +
        'modo mailto porque ESP_ENDPOINT está vazio em assets/rota-forms.js. ' +
        'Nenhum lead será capturado automaticamente.'
      );
    }
    if (!GA4_ID) {
      console.debug('[Rota com Família] GA4_ID vazio: eventos só aparecem no console.');
    }

    Consentimento.iniciar();
    iniciarBotaoZap();
    ligarCopiarCupom();
  });


  /* =============================================================================
     8. API PÚBLICA (mínima)
     Útil para um link "Gerenciar cookies" ou para disparar eventos de outros
     scripts. Ex.: <a href="#" data-abrir-cookies>Gerenciar cookies</a>
     ============================================================================= */
  window.RotaForms = {
    evento:            GA.evento,
    abrirBannerCookies: Consentimento.mostrarBanner,
    redefinirConsentimento: Consentimento.reabrir,
    consentimento:     Consentimento.ler,
    configurado:       function () { return { esp: !!ESP_ENDPOINT, ga4: !!GA4_ID }; }
  };

})();
