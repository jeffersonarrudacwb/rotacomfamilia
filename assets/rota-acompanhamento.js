/* =============================================================================
   Rota com Família — área de acompanhamento
   =============================================================================

   A página do cliente: ele digita o código do orçamento, vê o planejamento e
   marca as atrações que quer.

   ESTILO: ES5, var, sem arrow function, sem passo de build. É o mesmo do
   rota-forms.js, e por isso mesmo: dois arquivos na mesma pasta escritos em
   dialetos diferentes é como um deles acaba não sendo mantido.

   POR QUE NÃO REUSA O rota-forms.js

   Tentei. Não dá: aquele arquivo exporta só cinco coisas em window.RotaForms
   (evento, abrirBannerCookies, redefinirConsentimento, consentimento,
   configurado). mostrarMensagem, botaoOcupado, lerStorage e companhia são
   privados dentro da IIFE. E o lerStorage de lá é fixo em localStorage, que é
   a loja errada aqui. Então as poucas funções equivalentes estão reescritas
   embaixo, de propósito, e não por descuido.

   O formulário desta página NÃO tem data-origem, data-waitlist nem
   data-rota-form, e não vive dentro de #newsletter. São os quatro ganchos do
   SELETOR_FORMS do rota-forms.js: com qualquer um deles, aquele script
   capturaria o submit e mandaria este formulário para a /api/inscrever.php.

   REGRA QUE NÃO SE QUEBRA: nada que venha do servidor é escrito com innerHTML.
   Esta é a primeira página do site que mostra texto digitado por um usuário
   (a atração que o próprio cliente acrescenta), e textContent é o que faz um
   <script> digitado ali aparecer como texto em vez de rodar.
   ========================================================================== */
(function () {
  'use strict';

  var ENDPOINT = '/api/acompanhamento.php';
  var CHAVE    = 'rcf_ac_v1';
  var ZAP      = 'https://wa.me/5541988652343';

  var estado = {
    codigo:   null,
    versao:   0,
    editavel: false,
    dados:    null,
    sujo:     false
  };

  /* ---------------------------------------------------------------------------
     Guarda de sessão

     sessionStorage e não cookie. O site não grava nenhum cookie próprio hoje
     (a escolha do banner mora em localStorage), e um cookie de sessão seria o
     primeiro — além de trazer de volta a necessidade de defesa contra CSRF,
     que este desenho não tem justamente por não ter cookie.

     E morre ao fechar a aba, que é o certo num celular de família.

     O try/catch não é frescura: o Safari em janela anônima lança exceção só de
     encostar em sessionStorage.
     ------------------------------------------------------------------------ */
  function guardar(obj) {
    try {
      window.sessionStorage.setItem(CHAVE, JSON.stringify(obj));
      return true;
    } catch (e) { return false; }
  }
  function ler() {
    try {
      var s = window.sessionStorage.getItem(CHAVE);
      return s ? JSON.parse(s) : null;
    } catch (e) { return null; }
  }
  function esquecer() {
    try { window.sessionStorage.removeItem(CHAVE); } catch (e) {}
  }

  /* --------------------------------------------------------------------------
     Auxiliares de tela
     ------------------------------------------------------------------------ */
  function $(id) { return document.getElementById(id); }

  function mostrar(el, sim) {
    if (el) { el.hidden = !sim; }
  }

  /** Recado numa caixa, montado por textContent. Nunca innerHTML. */
  function recado(alvo, tipo, texto, comZap) {
    if (!alvo) { return; }
    var molde = $('tpl-recado');
    alvo.textContent = '';
    var no = molde.content.cloneNode(true);
    var caixa = no.querySelector('[data-c="caixa"]');
    var cores = {
      erro:    'border-red-500/30 bg-red-500/5 text-red-200',
      aviso:   'border-brand-orange/30 bg-brand-orange/5 text-brand-sky',
      sucesso: 'border-brand-fern/30 bg-brand-fern/5 text-brand-fern'
    };
    caixa.className += ' ' + (cores[tipo] || cores.aviso);
    no.querySelector('[data-c="texto"]').textContent = texto;
    if (comZap) {
      var a = document.createElement('a');
      a.href = ZAP;
      a.target = '_blank';
      a.rel = 'noopener';
      a.className = 'inline-block mt-2 underline decoration-brand-orange/50 underline-offset-2';
      a.textContent = 'Falar comigo no WhatsApp';
      caixa.appendChild(a);
    }
    alvo.appendChild(no);
    mostrar(alvo, true);
  }

  function ocupado(btn, sim, texto) {
    if (!btn) { return; }
    if (sim) {
      btn.setAttribute('data-rcf-texto', btn.textContent);
      btn.textContent = texto || 'Enviando…';
      btn.setAttribute('aria-busy', 'true');
      btn.disabled = true;
    } else {
      var antigo = btn.getAttribute('data-rcf-texto');
      if (antigo) { btn.textContent = antigo; }
      btn.removeAttribute('aria-busy');
      btn.disabled = false;
    }
  }

  /** '2026-11-23 01:30' -> '23/11, 01h30'. Sem Date: a string já é hora local
      do aeroporto, e passar por Date aplicaria o fuso do aparelho em cima. */
  function quando(s) {
    if (!s) { return ''; }
    var m = /^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})/.exec(s);
    if (!m) { return s; }
    return m[3] + '/' + m[2] + ', ' + m[4] + 'h' + m[5];
  }

  function duracao(min) {
    if (!min) { return ''; }
    var h = Math.floor(min / 60), r = min % 60;
    return h + 'h' + (r < 10 ? '0' : '') + r;
  }

  function dia(s) {
    if (!s) { return ''; }
    var m = /^(\d{4})-(\d{2})-(\d{2})/.exec(s);
    return m ? m[3] + '/' + m[2] : s;
  }

  /* --------------------------------------------------------------------------
     Conversa com o servidor
     ------------------------------------------------------------------------ */
  function chamar(corpo) {
    var ctrl = typeof AbortController === 'function' ? new AbortController() : null;
    var relogio = setTimeout(function () { if (ctrl) { ctrl.abort(); } }, 20000);
    return fetch(ENDPOINT, {
      method:      'POST',
      credentials: 'omit',
      headers:     { 'Content-Type': 'application/json' },
      body:        JSON.stringify(corpo),
      signal:      ctrl ? ctrl.signal : undefined
    }).then(function (r) {
      clearTimeout(relogio);
      return r.json().catch(function () { return {}; }).then(function (j) {
        return { http: r.status, corpo: j };
      });
    });
  }

  function uuid() {
    if (window.crypto && typeof window.crypto.randomUUID === 'function') {
      return window.crypto.randomUUID();
    }
    var b = new Uint8Array(16);
    (window.crypto || {}).getRandomValues
      ? window.crypto.getRandomValues(b)
      : (function () { for (var i = 0; i < 16; i++) { b[i] = Math.floor(Math.random() * 256); } })();
    var h = '';
    for (var i = 0; i < 16; i++) { h += ('0' + b[i].toString(16)).slice(-2); }
    return h;
  }

  /* --------------------------------------------------------------------------
     Desenho do planejamento
     ------------------------------------------------------------------------ */
  function desenharVoos(voos) {
    var corpo = $('ac-voos');
    corpo.textContent = '';
    voos.forEach(function (v) {
      if (v.tipo !== 'voo') {
        var n = $('tpl-voo-nota').content.cloneNode(true);
        var t = v.observacao || '';
        if (!t) {
          t = v.tipo === 'conexao' ? 'Conexão' : 'Parada';
        }
        n.querySelector('[data-c="nota"]').textContent = t;
        corpo.appendChild(n);
        return;
      }
      var l = $('tpl-voo').content.cloneNode(true);
      l.querySelector('[data-c="voo"]').textContent =
        [v.companhia, v.numero_voo].filter(Boolean).join(' ');
      l.querySelector('[data-c="trecho"]').textContent =
        (v.origem_iata || '') + ' → ' + (v.destino_iata || '');
      l.querySelector('[data-c="partida"]').textContent = quando(v.partida_local);
      l.querySelector('[data-c="chegada"]').textContent = quando(v.chegada_local);
      l.querySelector('[data-c="duracao"]').textContent = duracao(v.duracao_min);
      corpo.appendChild(l);
    });
  }

  function marcarBotoes(caixa, resposta) {
    var sim = caixa.querySelector('[data-c="sim"]');
    var nao = caixa.querySelector('[data-c="nao"]');
    sim.classList.toggle('chip-active', resposta === 'sim');
    nao.classList.toggle('chip-active', resposta === 'nao');
    sim.setAttribute('aria-pressed', resposta === 'sim' ? 'true' : 'false');
    nao.setAttribute('aria-pressed', resposta === 'nao' ? 'true' : 'false');
    var q = caixa.querySelector('[data-c="pessoas"]');
    // Quantidade só faz sentido no que ele quer fazer.
    q.disabled = resposta !== 'sim';
    q.style.opacity = resposta === 'sim' ? '1' : '0.35';
  }

  function desenharAtracao(a, cidadeId) {
    var no = $('tpl-atracao').content.cloneNode(true);
    var caixa = no.querySelector('div');
    caixa.setAttribute('data-atracao', String(a.id));
    caixa.setAttribute('data-cidade', String(cidadeId));

    no.querySelector('[data-c="nome"]').textContent = a.nome;

    var selo = no.querySelector('[data-c="selo"]');
    if (a.origem === 'cliente') {
      selo.textContent = 'Você acrescentou';
      mostrar(selo, true);
    } else if (a.preco_tipo === 'gratuita') {
      selo.textContent = 'Gratuita';
      mostrar(selo, true);
    }
    if (a.sazonal) { mostrar(no.querySelector('[data-c="selo-sazonal"]'), true); }

    var campos = [
      ['descricao', a.descricao],
      ['horario',   a.horario],
      ['janela',    a.janela],
      ['detalhes',  a.detalhes]
    ];
    campos.forEach(function (par) {
      var el = no.querySelector('[data-c="' + par[0] + '"]');
      if (par[1]) { el.textContent = par[1]; } else { el.remove(); }
    });

    var preco = a.preco_texto;
    if (preco) {
      var p = document.createElement('p');
      p.className = 'mt-1.5 text-xs text-brand-sky';
      p.textContent = preco;
      no.querySelector('[data-c="nome"]').parentNode.parentNode.appendChild(p);
    }

    var q = no.querySelector('[data-c="pessoas"]');
    if (a.escolha) {
      q.value = a.escolha.pessoas == null ? '' : String(a.escolha.pessoas);
    }
    marcarBotoes(caixa, a.escolha ? a.escolha.resposta : null);
    return no;
  }

  function desenharCidades(cidades) {
    var alvo = $('ac-cidades');
    alvo.textContent = '';
    cidades.forEach(function (c) {
      var no = $('tpl-cidade').content.cloneNode(true);
      var bloco = no.querySelector('div');
      bloco.setAttribute('data-cidade', String(c.id));
      no.querySelector('[data-c="nome"]').textContent = c.nome + ', ' + c.pais;

      var estadia = '';
      if (c.noites) {
        estadia = c.noites + (c.noites === 1 ? ' noite' : ' noites');
      }
      if (c.chegada) {
        estadia = (estadia ? estadia + ' · ' : '')
                + dia(c.chegada) + (c.saida ? ' a ' + dia(c.saida) : '');
      }
      no.querySelector('[data-c="estadia"]').textContent = estadia;

      var nota = no.querySelector('[data-c="nota"]');
      if (c.nota) { nota.textContent = c.nota; } else { nota.remove(); }

      var lista = no.querySelector('[data-c="lista"]');
      c.atracoes.forEach(function (a) { lista.appendChild(desenharAtracao(a, c.id)); });

      alvo.appendChild(no);
    });
  }

  function desenhar(d) {
    estado.dados    = d;
    estado.versao   = d.versao;
    estado.editavel = !!d.planejamento.editavel;

    $('ac-titulo').textContent = d.planejamento.titulo;
    var per = [];
    if (d.planejamento.inicio) {
      per.push(dia(d.planejamento.inicio) + ' a ' + dia(d.planejamento.fim));
    }
    if (d.planejamento.passageiros) {
      per.push(d.planejamento.passageiros
        + (d.planejamento.passageiros === 1 ? ' passageiro' : ' passageiros'));
    }
    $('ac-periodo').textContent = per.join(' · ');
    $('ac-descricao').textContent = d.planejamento.descricao || '';

    desenharVoos(d.voos || []);
    desenharCidades(d.cidades || []);

    // Ler é liberado em qualquer etapa: quem respondeu tem direito de rever o
    // que respondeu. O que a etapa tranca é gravar, e quem decide isso é o
    // servidor. Isto aqui só evita mostrar um botão que não vai funcionar.
    mostrar($('ac-rodape-salvar'), estado.editavel);
    if (!estado.editavel) {
      recado($('ac-aviso-etapa'), 'aviso',
        'Este planejamento já saiu da etapa de edição, então as respostas '
        + 'ficam só para consulta. Se precisar mudar alguma coisa, me chame.',
        true);
      travar();
    }

    mostrar($('entrada'), false);
    mostrar($('planejamento'), true);
    window.scrollTo(0, 0);
  }

  function travar() {
    var campos = $('ac-cidades').querySelectorAll('button, input');
    for (var i = 0; i < campos.length; i++) { campos[i].disabled = true; }
  }

  /* --------------------------------------------------------------------------
     Entrar
     ------------------------------------------------------------------------ */
  function entrar(codigo, botao) {
    ocupado(botao, true, 'Procurando…');
    mostrar($('ac-erro'), false);
    return chamar({ acao: 'abrir', codigo: codigo }).then(function (r) {
      ocupado(botao, false);
      if (r.http === 200 && r.corpo.ok) {
        estado.codigo = codigo;
        guardar({ codigo: codigo });
        desenhar(r.corpo);
        return;
      }
      esquecer();
      recado($('ac-erro'), 'erro',
        r.corpo.mensagem || 'Não consegui abrir agora.',
        r.http === 401 || r.http === 503);
    }).catch(function () {
      ocupado(botao, false);
      recado($('ac-erro'), 'erro',
        'Não consegui falar com o servidor. Confira a conexão e tente de novo.',
        true);
    });
  }

  /* --------------------------------------------------------------------------
     Salvar
     ------------------------------------------------------------------------ */
  function coletar() {
    var escolhas = [], novas = [];
    var caixas = $('ac-cidades').querySelectorAll('[data-atracao]');
    for (var i = 0; i < caixas.length; i++) {
      var c = caixas[i];
      var id = parseInt(c.getAttribute('data-atracao'), 10);
      var sim = c.querySelector('[data-c="sim"]').classList.contains('chip-active');
      var nao = c.querySelector('[data-c="nao"]').classList.contains('chip-active');
      if (!sim && !nao) { continue; }          // não respondida fica sem linha
      var q = c.querySelector('[data-c="pessoas"]').value.trim();
      if (id < 0) {
        novas.push({
          cidade_id: parseInt(c.getAttribute('data-cidade'), 10),
          nome:      c.getAttribute('data-nome') || ''
        });
        continue;
      }
      escolhas.push({
        atracao_id: id,
        resposta:   sim ? 'sim' : 'nao',
        pessoas:    (sim && q !== '') ? parseInt(q, 10) : null
      });
    }
    return { escolhas: escolhas, novas: novas };
  }

  function salvar() {
    var btn = $('ac-salvar');
    var junto = coletar();
    ocupado(btn, true, 'Salvando…');
    mostrar($('ac-msg'), false);

    return chamar({
      acao:     'salvar',
      codigo:   estado.codigo,
      versao:   estado.versao,
      envio_id: uuid(),
      escolhas: junto.escolhas,
      novas:    junto.novas
    }).then(function (r) {
      ocupado(btn, false);

      if (r.http === 200 && r.corpo.ok) {
        estado.versao = r.corpo.versao;
        estado.sujo = false;
        // As atrações novas voltam com id de verdade. Sem trocar, um segundo
        // salvamento mandaria de novo as mesmas e criaria duplicata.
        (r.corpo.criadas || []).forEach(function (nova) {
          var prov = $('ac-cidades').querySelector('[data-nome="' + nova.nome + '"]');
          if (prov) {
            prov.setAttribute('data-atracao', String(nova.id));
            prov.removeAttribute('data-nome');
          }
        });
        $('ac-estado').textContent = 'Salvo agora.';
        recado($('ac-msg'), 'sucesso', r.corpo.mensagem);
        return;
      }

      if (r.http === 409) {
        // NÃO limpa nada. O que ele marcou fica na tela: perder vinte minutos
        // de marcação sem explicação é o pior desfecho possível aqui.
        recado($('ac-msg'), 'aviso', r.corpo.mensagem, true);
        if (r.corpo.motivo === 'etapa_fechada') {
          estado.editavel = false;
          mostrar($('ac-rodape-salvar'), false);
          travar();
        }
        return;
      }

      recado($('ac-msg'), 'erro',
        r.corpo.mensagem || 'Não consegui salvar agora.', true);
    }).catch(function () {
      ocupado(btn, false);
      recado($('ac-msg'), 'erro',
        'A conexão caiu antes de eu conseguir salvar. Suas respostas continuam '
        + 'na tela: tente de novo.', true);
    });
  }

  /* --------------------------------------------------------------------------
     Ligação dos eventos
     ------------------------------------------------------------------------ */
  function ligar() {
    var form = $('ac-form');
    if (!form) { return; }   // não é esta página

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var campo = $('ac-codigo');
      var codigo = campo.value.trim();
      if (!codigo) {
        recado($('ac-erro'), 'erro', 'Digite o código que eu te mandei.');
        campo.focus();
        return;
      }
      entrar(codigo, $('ac-entrar'));
    });

    $('ac-sair').addEventListener('click', function () {
      esquecer();
      window.location.reload();
    });

    $('ac-salvar').addEventListener('click', salvar);

    // Um listener só, por delegação, para marcar/desmarcar e acrescentar. Com
    // ~60 atrações, ligar três listeners em cada uma seria 180 a atualizar toda
    // vez que a lista muda.
    $('ac-cidades').addEventListener('click', function (e) {
      var alvo = e.target;

      var botao = alvo.closest ? alvo.closest('[data-c="sim"], [data-c="nao"]') : null;
      if (botao && !botao.disabled) {
        var caixa = botao.closest('[data-atracao]');
        var quer = botao.getAttribute('data-c');
        var jaEstava = botao.classList.contains('chip-active');
        marcarBotoes(caixa, jaEstava ? null : quer);   // clicar de novo desmarca
        estado.sujo = true;
        $('ac-estado').textContent = 'Há mudanças não salvas.';
        return;
      }

      var add = alvo.closest ? alvo.closest('[data-c="nova-add"]') : null;
      if (add && !add.disabled) {
        var bloco = add.closest('[data-cidade]');
        var campo = bloco.querySelector('[data-c="nova-nome"]');
        var nome = campo.value.trim();
        if (!nome) { campo.focus(); return; }
        var cidadeId = parseInt(bloco.getAttribute('data-cidade'), 10);
        // id negativo provisório: o servidor devolve o de verdade ao salvar.
        var no = desenharAtracao({
          id: -Date.now(), origem: 'cliente', nome: nome,
          escolha: { resposta: 'sim', pessoas: null }
        }, cidadeId);
        var criada = no.querySelector('[data-atracao]');
        criada.setAttribute('data-nome', nome);
        bloco.querySelector('[data-c="lista"]').appendChild(no);
        campo.value = '';
        estado.sujo = true;
        $('ac-estado').textContent = 'Há mudanças não salvas.';
      }
    });

    $('ac-cidades').addEventListener('input', function () {
      estado.sujo = true;
      $('ac-estado').textContent = 'Há mudanças não salvas.';
    });

    window.addEventListener('beforeunload', function (e) {
      if (estado.sujo) { e.preventDefault(); e.returnValue = ''; }
    });

    // Voltou de um recarregamento com o código ainda na sessão.
    var guardado = ler();
    if (guardado && guardado.codigo) {
      $('ac-codigo').value = guardado.codigo;
      entrar(guardado.codigo, $('ac-entrar'));
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ligar);
  } else {
    ligar();
  }
})();
