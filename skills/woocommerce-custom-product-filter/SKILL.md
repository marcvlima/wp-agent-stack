---
name: woocommerce-custom-product-filter
description: Guia obrigatório para adicionar QUALQUER filtro customizado ao bloco Product Filters do WooCommerce (busca por nome/texto, meta de produto, ou qualquer critério que o WooCommerce não oferece nativamente) mantendo navegação 100% AJAX sem reload, com chip sincronizado em "Filtros ativos". Use SEMPRE que precisar criar um novo filtro na loja (archives da loja/categoria/marca) que não seja um dos blocos nativos (product-filter-attribute, -taxonomy, -price, -status, -rating). Impede reload de página e os bugs de sincronização de chip.
---

# WooCommerce — Filtro Customizado no Product Filters (AJAX, sem reload)

**Quando usar:** qualquer pedido de "adicionar um filtro X na loja" onde X **não** é um
atributo/taxonomia/preço/estoque/rating nativo — por exemplo: **busca por nome/texto**,
filtro por meta customizado, por faixa de data, por qualquer critério calculado.

**Regra inegociável (`.agents/AGENTS.md`):** a filtragem **NÃO pode recarregar a
página**. Nunca use o bloco legado `woocommerce/product-search` dentro do container de
filtros — ele força page reload e é incompatível com a Interactivity API.

Este guia foi extraído da implementação real e validada da **busca por nome** no tema
`arabian-mirage`. Siga os 6 passos na ordem. O código de referência completo está em
[`reference/`](reference/).

---

## Por que a abordagem ingênua FALHA (leia antes de codar)

Três armadilhas que quebram qualquer tentativa "simples" — todas verificadas no
código-fonte do WooCommerce instalado, não na documentação:

1. **`window.wp.interactivity` NÃO existe.** A Interactivity API é um ES **script
   module**; não é exposta no global `window.wp`. Qualquer navegação escrita num
   **script clássico** (`wp_enqueue_script`) cai no fallback `window.location.href` =
   **reload**. A navegação client-side **precisa** morar num **script module**
   (`wp_enqueue_script_module`), que é o único contexto onde o import map resolve
   `@wordpress/interactivity-router`.

2. **Os chips de "Filtros ativos" são estado client-side, não HTML do servidor.** Eles
   renderizam de `data-wp-each="state.activeFilters"`, cujo getter lê `getContext()`
   (contexto **persistido no cliente**). Numa navegação AJAX o `data-wp-context` inicial
   **não é relido** → o chip do seu filtro **não aparece/some sem um refresh completo**.
   Os filtros nativos aparecem na hora porque a ação `toggleFilter` **muta**
   `context.activeFilters` **antes** de navegar. Você tem que fazer o mesmo.

3. **O `navigate()` nativo mantém o SEU parâmetro na URL.** Ao remover o chip pelo
   botão × nativo, `removeActiveFilter` reconstrói a URL a partir da `canonicalUrl`, que
   **conserva** parâmetros que o WC não reconhece (ex: `filter_nome`). Resultado: o chip
   some mas a grade continua filtrada. É preciso **interceptar** a remoção do seu chip.

**Solução correta:** navegar de um **script module** + **estender o store
`woocommerce/product-filters`** (ele **não** é *locked*) de forma **puramente aditiva**
(só chaves novas — assim a ordem de carregamento dos módulos é irrelevante; sobrescrever
chaves do WC é sensível à ordem e **proibido**).

---

## Passo a passo

Nomes de exemplo (troque pelo seu filtro): parâmetro `filter_nome`, tipo de chip
`am-search`, bloco `arabian-mirage/product-filter-search`.

### 1. PHP — Query var + aplicação na query principal
Registre uma query var própria (NUNCA use `s` nativo, que marca a página como busca e
força reload) e aplique-a em `woocommerce_product_query`, **escopado** aos archives da
loja. Ver [`reference/loja-blocos.php`](reference/loja-blocos.php) (seção "query").

### 2. PHP — Chip em "Filtros ativos" via hook público
Use o filtro **público** `woocommerce_blocks_product_filters_selected_items` (o mesmo que
TODOS os filtros nativos usam — não é um componente WC, é um `add_filter`). Adicione um
item com `type` de **namespace próprio** (ex: `am-search`), `value` e `activeLabel`.
O getter nativo `get activeFilters()` filtra por `!!value`, ordena por label e injeta
`uid` automaticamente — seu item flui igual aos nativos.

### 3. PHP — Bloco dinâmico do controle + diretivas Interactivity
Registre um bloco próprio do tema (`register_block_type` com `render_callback`;
**não** estenda classes do WooCommerce). No HTML do controle, adicione as diretivas:
- no wrapper: `data-wp-init="callbacks.amStashContext"` (guarda o contexto reativo);
- no input/controle: `data-wp-on--input="actions.amSearchInput"` e
  `data-wp-on--keydown="actions.amSearchKeydown"`.
O namespace `woocommerce/product-filters` é **herdado** do wrapper nativo (o bloco é
renderizado dentro dele) — não precisa (nem deve) declarar `data-wp-interactive` próprio.

### 4. PHP — Enfileirar o JS como SCRIPT MODULE
```php
wp_enqueue_script_module(
    'am-loja-search',
    $uri . '/assets/loja-search.js',
    array( '@wordpress/interactivity', '@wordpress/interactivity-router' ),
    (string) filemtime( $js_module )
);
```
`wp_enqueue_script` (clássico) aqui **não funciona** — ver armadilha #1.

### 5. JS (módulo) — Navegação AJAX + extensão aditiva do store
Ver [`reference/loja-search.js`](reference/loja-search.js) na íntegra. Pontos-chave:
- Navegar com `const { actions } = await import('@wordpress/interactivity-router');
  await actions.navigate(href);`
- `store('woocommerce/product-filters', { actions: {...}, callbacks: {...} })` **só com
  chaves novas**. Nas actions (que rodam em escopo), `getContext()` funciona e você muta
  `context.activeFilters` para o chip aparecer na hora; a navegação é debounced.
- **Remoção do chip nativo:** listener no `document` em **fase de captura**, filtrando
  pelo seu `type` lido do `data-wp-context` do botão; `stopImmediatePropagation()` +
  `preventDefault()`, muta `activeFilters` (via contexto guardado no passo 3) e navega
  sem o seu parâmetro.

### 6. Template part + CSS
Adicione o bloco no `parts/loja-filtros.html` na posição desejada e estilize o controle
para casar com os demais filtros. Ver [`reference/`](reference/).

---

## Checklist de validação (obrigatório antes de entregar)

Servidor (via `curl` no container):
- [ ] `php -l` sem erro no arquivo de blocos.
- [ ] `?<param>=<termo>` filtra a grade (compare contagem de produtos com/sem filtro e
      com um termo inexistente → zero).
- [ ] O chip aparece no HTML com `data-wp-context` contendo seu `type`.
- [ ] `<script type="module">` do seu JS presente + import map com
      `@wordpress/interactivity-router`.

Navegador (teste manual — a Interactivity API só roda no browser):
- [ ] Digitar/selecionar → chip aparece **na hora**, grade filtra **sem reload** (Network
      mostra `fetch`, não novo document load).
- [ ] Limpar o controle → chip some e parâmetro sai da URL, sem reload.
- [ ] × do chip nativo → some e parâmetro sai da URL, sem reload.
- [ ] Abrir a URL com o parâmetro **direto** e clicar no × → remove corretamente
      (valida o `data-wp-init`).
- [ ] Filtros nativos (marca/gênero/preço) continuam funcionando isolados e **combinados**
      com o seu filtro.

---

## Armadilhas específicas do ambiente

- **OPcache:** após editar PHP, **reinicie o container WordPress** antes de testar
  (`docker compose restart wordpress`), senão testa código antigo. Ver memória
  `docker-restart-opcache`.
- **Migrations:** se a mudança for só arquivos de tema (PHP/JS/CSS), **não** precisa de
  migration. Se tocar `wp_options`/banco (ex: registrar um atributo), aí **sim** crie
  script em `bin/migrations/` conforme `.agents/AGENTS.md`.
- **Não sobrescreva chaves do store WC** (só adicione). **Não** edite arquivos do plugin
  WooCommerce (não são versionados no deploy e somem no próximo update).

Referência de fundo: memória `wc-product-filters-custom-search-block` e o plano
`docs/plans/arabian-mirage-filtros-blocos-loja.md`.
