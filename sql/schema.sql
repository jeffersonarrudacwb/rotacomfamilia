-- =============================================================================
-- Rota com Familia - area de acompanhamento do cliente
-- =============================================================================
--
-- Rode uma vez, no phpMyAdmin do cPanel, no banco criado para isto.
-- Nao ha migracao automatica: este arquivo e a verdade do esquema.
--
-- ANTES DE RODAR, confira a versao do servidor em phpMyAdmin > pagina inicial.
-- Duas coisas dependem dela:
--
--   * CHECK so e OBRIGADO a partir do MySQL 8.0.16 e do MariaDB 10.2.1. Em
--     MySQL 5.7 ele e aceito na sintaxe e ignorado em silencio. Por isso toda
--     regra que aparece como CHECK aqui esta TAMBEM validada no PHP. O CHECK e
--     cinto, e o PHP e o suspensorio, e o suspensorio e que segura.
--
--   * utf8mb4_unicode_ci em vez de utf8mb4_0900_ai_ci de proposito: a 0900 nao
--     existe no MariaDB, e nao da para saber daqui qual dos dois a HostGator
--     serve.
--
-- utf8mb4 e nao utf8: nao e estetica. O "utf8" do MySQL guarda 3 bytes por
-- caractere e nao cabe emoji. O cliente VAI escrever "Museu do Louvre 😍" no
-- campo de atracao, e com utf8 a linha e cortada no emoji.
--
-- POR QUE O CODIGO NAO ESTA AQUI EM CLARO
--
-- codigo_hash guarda SHA-256(pimenta || codigo), com a pimenta no
-- rota-config.php, um nivel acima da raiz do site. Sem isso, um dump vazado
-- entrega todos os codigos: sao 50 bits, e 2^50 SHA-256 e questao de horas de
-- GPU. Com a pimenta fora do banco, o dump sozinho nao vale nada.
--
-- O preco disso e real e precisa estar dito: o codigo fica IRRECUPERAVEL do
-- banco. Cliente que perde o codigo recebe outro, e o antigo e revogado.
-- =============================================================================

SET NAMES utf8mb4;
SET time_zone = '-03:00';


-- -----------------------------------------------------------------------------
-- 1. planejamento - uma linha por viagem de cliente
-- -----------------------------------------------------------------------------
CREATE TABLE rcf_planejamento (
  id                 INT UNSIGNED     NOT NULL AUTO_INCREMENT,

  -- SHA-256(pimenta || codigo_normalizado). Calculado no PHP, nunca com
  -- SHA2() no SQL: a funcao no SQL poe a pimenta no slow query log.
  codigo_hash        BINARY(32)       NOT NULL,

  -- Para VOCE achar a linha no phpMyAdmin. NAO pode conter pedaco do codigo:
  -- guardar "os 4 primeiros caracteres como dica" entregaria 20 dos 50 bits.
  apelido            VARCHAR(60)      NOT NULL,

  cliente_nome       VARCHAR(120)     NOT NULL,
  titulo             VARCHAR(160)     NOT NULL,
  descricao          TEXT             NULL,
  passageiros        TINYINT UNSIGNED NOT NULL DEFAULT 1,

  -- A trava de edicao. ENUM e nao tabela de apoio: assim uma etapa digitada
  -- errado nao chega a existir no armazenamento.
  --
  -- REGRA: valor novo entra sempre NO FIM. ENUM e posicional, e inserir no
  -- meio remapeia em silencio as linhas que ja existem.
  etapa              ENUM('proposta','emissao','hospedagem','atracoes',
                          'roteiro','concluida','arquivada')
                                      NOT NULL DEFAULT 'hospedagem',

  data_inicio        DATE             NULL,
  data_fim           DATE             NULL,

  -- Trava otimista: sobe a cada gravacao aceita. Se o cliente abriu em dois
  -- aparelhos, o segundo a salvar leva 409 em vez de apagar o primeiro.
  versao             INT UNSIGNED     NOT NULL DEFAULT 1,

  codigo_emitido_em  DATETIME         NOT NULL,
  codigo_revogado_em DATETIME         NULL,

  -- Prazo duro, independente da etapa. Viagem que acaba em 09/12/2026 nao tem
  -- por que abrir em 2029 so porque alguem esqueceu de mudar a etapa.
  expira_em          DATETIME         NULL,

  ultimo_acesso_em   DATETIME         NULL,
  acessos            INT UNSIGNED     NOT NULL DEFAULT 0,

  criado_em          TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  atualizado_em      TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                      ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (id),
  UNIQUE KEY uq_codigo (codigo_hash),
  -- Parece redundante com a PK. Nao e: e o alvo das chaves estrangeiras
  -- compostas la embaixo, e o InnoDB exige indice unico na lista referenciada.
  UNIQUE KEY uq_plan_escopo (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- NAO EXISTEM AQUI, e e decisao e nao esquecimento: CPF, passaporte, email,
-- telefone, data de nascimento, login de programa de milhas. Nada disso e
-- preciso para a pessoa marcar se quer ir ao Empire State. O que este banco
-- guarda ja esta coberto pela base legal que a privacidade.html declara no §3
-- (art. 7o, V) e pelo prazo do §5. Acrescentar CPF mudaria os dois.


-- -----------------------------------------------------------------------------
-- 2. voo - os trechos, na ordem em que acontecem
-- -----------------------------------------------------------------------------
CREATE TABLE rcf_voo (
  id                INT UNSIGNED      NOT NULL AUTO_INCREMENT,
  planejamento_id   INT UNSIGNED      NOT NULL,
  ordem             SMALLINT UNSIGNED NOT NULL,

  -- 'conexao' e 'estadia' entram na MESMA lista ordenada dos voos, que e como
  -- o PDF da conferencia ja mostra ("Conexao em Tocumen - 11h36 de espera").
  -- Sem isto seriam duas tabelas e uma intercalacao no PHP.
  tipo              ENUM('voo','conexao','estadia') NOT NULL DEFAULT 'voo',

  -- O agrupamento que o cliente ja conhece do PDF: os bilhetes 1 e 4 sao um
  -- bilhete so com dois voos.
  bilhete           TINYINT UNSIGNED  NULL,

  companhia         VARCHAR(40)       NULL,
  numero_voo        VARCHAR(10)       NULL,
  origem_iata       CHAR(3)           NULL,
  destino_iata      CHAR(3)           NULL,

  -- Hora local de cada aeroporto, igual ao cartao de embarque. A duracao vai
  -- GUARDADA e nao calculada: derivar duracao de dois horarios locais em fusos
  -- diferentes e onde nascem os bugs de fuso.
  partida_local     DATETIME          NULL,
  chegada_local     DATETIME          NULL,
  duracao_min       SMALLINT UNSIGNED NULL,

  observacao        VARCHAR(255)      NULL,

  PRIMARY KEY (id),
  KEY ix_voo_plan (planejamento_id, ordem),
  CONSTRAINT fk_voo_plan FOREIGN KEY (planejamento_id)
    REFERENCES rcf_planejamento (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- -----------------------------------------------------------------------------
-- 3. cidade - as paradas, por planejamento
-- -----------------------------------------------------------------------------
--
-- Por que cidade por planejamento e nao um dicionario global de cidades: o Boni
-- passa DUAS vezes pela Cidade do Panama, uma escala de 11h36 na ida e uma
-- noite na volta, e a lista de atracoes das duas e diferente. Duas linhas com
-- ordem 1 e 5 resolvem isso sem caso especial. Um dicionario compartilhado
-- precisaria de tabela de ligacao para dizer "a mesma cidade, duas vezes, com
-- listas diferentes", num site que vai ter cliente em numero de um digito.
--
-- REGRA do que merece uma linha aqui: o cliente consegue sair do aeroporto.
-- Panama com 11h36, sim. Bogota com 1h20 internacional, NAO - aquilo e uma
-- linha de rcf_voo com tipo='conexao'. Errar isso mostra ao cliente uma secao
-- "atracoes em Bogota" vazia, que ele le como defeito.
-- -----------------------------------------------------------------------------
CREATE TABLE rcf_cidade (
  id              INT UNSIGNED      NOT NULL AUTO_INCREMENT,
  planejamento_id INT UNSIGNED      NOT NULL,
  ordem           SMALLINT UNSIGNED NOT NULL,
  nome            VARCHAR(80)       NOT NULL,
  pais            VARCHAR(60)       NOT NULL,
  chegada         DATE              NULL,
  saida           DATE              NULL,
  noites          TINYINT UNSIGNED  NULL,
  nota            VARCHAR(255)      NULL,

  PRIMARY KEY (id),
  UNIQUE KEY uq_cidade_ordem (planejamento_id, ordem),
  UNIQUE KEY uq_cidade_escopo (id, planejamento_id),
  CONSTRAINT fk_cidade_plan FOREIGN KEY (planejamento_id)
    REFERENCES rcf_planejamento (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- -----------------------------------------------------------------------------
-- 4. atracao - o que eu cadastrei E o que o cliente acrescentou
-- -----------------------------------------------------------------------------
CREATE TABLE rcf_atracao (
  id              INT UNSIGNED      NOT NULL AUTO_INCREMENT,
  planejamento_id INT UNSIGNED      NOT NULL,
  cidade_id       INT UNSIGNED      NOT NULL,

  -- Uma tabela so, com discriminador, e nao duas. Duas tabelas obrigariam a
  -- escolha a ter chave estrangeira polimorfica (tipo + id), que o InnoDB nao
  -- consegue garantir. Assim a integridade referencial e de verdade.
  --
  -- No endpoint, este campo e a string literal 'cliente' dentro do INSERT.
  -- Nunca uma variavel vinda do corpo da requisicao.
  origem          ENUM('curadoria','cliente') NOT NULL,

  nome            VARCHAR(120)      NOT NULL,
  descricao       VARCHAR(500)      NULL,
  horario         VARCHAR(160)      NULL,

  preco_tipo      ENUM('gratuita','paga','variavel') NOT NULL DEFAULT 'paga',
  -- Texto e nao numero, de proposito: preco de ingresso muda, e numero velho
  -- na frente do cliente e pior do que numero nenhum.
  preco_texto     VARCHAR(120)      NULL,

  sazonal         TINYINT(1)        NOT NULL DEFAULT 0,
  janela          VARCHAR(140)      NULL,
  detalhes        VARCHAR(600)      NULL,

  -- So para linha de curadoria. O endpoint RECUSA url em atracao do cliente:
  -- href com javascript: e XSS sem precisar de innerHTML nenhum.
  url             VARCHAR(300)      NULL,

  ordem           SMALLINT UNSIGNED NOT NULL DEFAULT 0,

  -- Apagar de verdade orfanaria o historico da escolha. Cliente que remove a
  -- propria atracao poe ativa=0. Nunca DELETE.
  ativa           TINYINT(1)        NOT NULL DEFAULT 1,

  criada_em       DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
  criada_ip_hash  BINARY(32)        NULL,

  PRIMARY KEY (id),
  UNIQUE KEY uq_atracao_escopo (id, planejamento_id),
  KEY ix_atracao_lista (planejamento_id, cidade_id, ativa, ordem),

  -- ESTA e a razao de planejamento_id existir aqui. Parece desnormalizacao,
  -- e o InnoDB recusando, no armazenamento, uma atracao que aponte para cidade
  -- de outro cliente. Vale mais do que lembrar de escrever o WHERE.
  CONSTRAINT fk_atracao_cidade
    FOREIGN KEY (cidade_id, planejamento_id)
    REFERENCES rcf_cidade (id, planejamento_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sem UNIQUE em (planejamento_id, cidade_id, nome). Tentador, mas sob
-- utf8mb4_unicode_ci, que ignora acento, "Cafe Central" e "Café Central"
-- colidem e o cliente levaria uma recusa que ele nao consegue explicar. A
-- checagem de repetido fica no PHP, como aviso amigavel e nao como bloqueio.


-- -----------------------------------------------------------------------------
-- 5. escolha - sim/nao e quantas pessoas
-- -----------------------------------------------------------------------------
CREATE TABLE rcf_escolha (
  id              INT UNSIGNED     NOT NULL AUTO_INCREMENT,
  planejamento_id INT UNSIGNED     NOT NULL,
  atracao_id      INT UNSIGNED     NOT NULL,

  -- Sao TRES estados com dois valores: 'sim', 'nao', e a AUSENCIA da linha,
  -- que quer dizer "ainda nao respondeu". Esse terceiro estado e util de
  -- verdade: permite dizer "faltam 4 atracoes" e separa "disse que nao" de
  -- "nem olhou".
  resposta        ENUM('sim','nao') NOT NULL,

  -- NULL = todos os passageiros. E o padrao pedido: quem nao marca quantidade
  -- esta falando pelo grupo inteiro.
  pessoas         TINYINT UNSIGNED NULL,

  atualizado_em   TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                   ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (id),
  UNIQUE KEY uq_escolha (planejamento_id, atracao_id),
  CONSTRAINT fk_escolha_atracao
    FOREIGN KEY (atracao_id, planejamento_id)
    REFERENCES rcf_atracao (id, planejamento_id) ON DELETE CASCADE,

  -- Limite grosseiro de sanidade. O limite que importa e pessoas <=
  -- planejamento.passageiros, que cruza tabela e nenhum CHECK expressa: esse
  -- vai no PHP. E, no MySQL 5.7, este CHECK aqui nem roda.
  CONSTRAINT ck_escolha_pessoas
    CHECK (pessoas IS NULL OR (pessoas >= 1 AND pessoas <= 20))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- -----------------------------------------------------------------------------
-- 6. salvamento - historico, idempotencia e desfazer
-- -----------------------------------------------------------------------------
--
-- Tres servicos pelo preco de uma tabela:
--
-- 1. HISTORICO. Voce vai reservar hotel com base no que o cliente marcou.
--    Quando ele disser "eu marquei o Empire State", da para responder olhando.
--
-- 2. IDEMPOTENCIA. envio_id e um UUID que o navegador gera por gravacao. Se a
--    conexao cair DEPOIS do commit, o cliente tenta de novo. Sem isto a segunda
--    tentativa levaria uma versao velha e um 409 sem explicacao. Com isto, o
--    endpoint reconhece o envio repetido e devolve o mesmo resultado.
--
-- 3. DESFAZER, quando algo der errado.
--
-- MEDIUMTEXT e nao JSON: o MariaDB apelida JSON para LONGTEXT com check, o
-- MySQL tem tipo de verdade, e esta coluna nunca e consultada por conteudo.
-- MEDIUMTEXT se comporta igual nos dois.
-- -----------------------------------------------------------------------------
CREATE TABLE rcf_salvamento (
  id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  planejamento_id INT UNSIGNED    NOT NULL,
  versao          INT UNSIGNED    NOT NULL,
  envio_id        CHAR(36)        NOT NULL,
  payload         MEDIUMTEXT      NOT NULL,
  ip_hash         BINARY(32)      NULL,
  criado_em       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (id),
  UNIQUE KEY uq_envio (planejamento_id, envio_id),
  KEY ix_salv_plan (planejamento_id, versao),
  CONSTRAINT fk_salv_plan FOREIGN KEY (planejamento_id)
    REFERENCES rcf_planejamento (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- -----------------------------------------------------------------------------
-- 7. freio - limitador de tentativas
-- -----------------------------------------------------------------------------
--
-- Substitui o limitador de arquivo do api/inscrever.php, que tem quatro
-- defeitos conhecidos e um deles e fatal:
--
--   * LOCK_EX no file_put_contents tranca so a ESCRITA. Duas requisicoes
--     simultaneas leem 4, ambas concluem 4 < 5, ambas gravam 5. Sob enxurrada
--     ele degrada para nenhum limite.
--   * sys_get_temp_dir() em hospedagem compartilhada e limpo de tempos em
--     tempos, o que zera todos os contadores.
--   * sha1($ip) sem pimenta e o IP do visitante a uma rainbow table de
--     distancia, num diretorio legivel por todos.
--   * Sem normalizacao de IPv6: um /64 da 1,8 x 10^19 "IPs" diferentes e o
--     limitador conta cada um separado, ou seja, e contornado por completo.
--
-- Aqui a soma e a virada de janela acontecem em UMA instrucao, sob bloqueio de
-- linha do InnoDB na chave primaria. Nenhuma tentativa deixa de ser contada.
-- -----------------------------------------------------------------------------
CREATE TABLE rcf_freio (
  chave         VARBINARY(64)     NOT NULL,
  janela_inicio DATETIME          NOT NULL,
  batidas       SMALLINT UNSIGNED NOT NULL DEFAULT 0,
  bloqueado_ate DATETIME          NULL,
  atualizado_em TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP
                                  ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (chave),
  KEY ix_freio_limpeza (atualizado_em)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- -----------------------------------------------------------------------------
-- 8. tentativa - o registro, para saber depois
-- -----------------------------------------------------------------------------
--
-- Separada do freio porque respondem perguntas diferentes: o freio e contador
-- vivo, lido no caminho quente. Esta aqui e para olhar depois ("alguem tentou
-- adivinhar codigo em marco?").
--
-- O IP entra so como hash com pimenta, entao isto NAO e um registro de IP em
-- claro. Fica dentro do que a privacidade.html ja declara no §3 sobre registro
-- de acesso (Marco Civil art. 15), sem redacao nova. Limpeza aos 90 dias.
-- -----------------------------------------------------------------------------
CREATE TABLE rcf_tentativa (
  id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  ip_hash         BINARY(32)      NOT NULL,
  acao            ENUM('abrir','salvar','exportar') NOT NULL,
  resultado       ENUM('ok','codigo_invalido','formato_invalido',
                       'etapa_fechada','conflito','bloqueado','erro') NOT NULL,
  planejamento_id INT UNSIGNED    NULL,
  criado_em       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY ix_tent_limpeza (criado_em),
  KEY ix_tent_plan (planejamento_id, criado_em)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
