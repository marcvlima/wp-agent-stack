/**
 * Busca por nome da loja — navegação 100% AJAX (sem reload).  ·  Arabian Mirage
 *
 * Este arquivo é enfileirado como SCRIPT MODULE (wp_enqueue_script_module).
 * Só nesse contexto o import map do WordPress resolve
 * `@wordpress/interactivity` e `@wordpress/interactivity-router` — os mesmos
 * módulos que os filtros nativos do WooCommerce usam para navegar sem recarregar.
 *
 * ── Por que estender o store do WooCommerce em vez de só manipular o DOM ──────
 * Os chips de "Filtros ativos" são renderizados a partir do ESTADO client-side
 * da Interactivity API (`data-wp-each="state.activeFilters"`), e esse estado NÃO
 * é re-sincronizado do servidor numa navegação AJAX (o `data-wp-context` inicial
 * não é relido). Por isso, para o chip aparecer/sumir sem refresh, precisamos
 * MUTAR `context.activeFilters` no store `woocommerce/product-filters` — é o que
 * a própria ação nativa `toggleFilter` faz. O store não é "locked", então
 * estendê-lo é seguro. Só adicionamos chaves NOVAS (nunca sobrescrevemos as do
 * WC), então a ordem de carregamento dos módulos é irrelevante.
 */

import { store, getContext } from '@wordpress/interactivity';

const SEARCH_PARAM = 'filter_nome';
const SEARCH_TYPE = 'am-search';
const CHIP_REMOVE_SELECTOR = '.wc-block-product-filter-removable-chips__remove';
const DEBOUNCE_MS = 450;

let debounceTimer = null;
// Referência ao contexto reativo do wrapper de filtros. Guardada por uma
// diretiva data-wp-init para que o listener de remoção do chip (que roda fora
// do escopo da Interactivity) também consiga mutar activeFilters.
let stashedContext = null;

/** Navega client-side pela mesma via dos filtros nativos do WooCommerce. */
async function routerNavigate( href ) {
	const { actions } = await import( '@wordpress/interactivity-router' );
	await actions.navigate( href );
}

/** Monta a URL alvo com (ou sem) o termo de busca, resetando a paginação. */
function buildUrl( term ) {
	const url = new URL( window.location.href );
	if ( term ) {
		url.searchParams.set( SEARCH_PARAM, term );
	} else {
		url.searchParams.delete( SEARCH_PARAM );
	}
	url.searchParams.delete( 'product-page' );
	url.searchParams.delete( 'paged' );
	return url;
}

/** Reconcilia o chip "Nome: …" no activeFilters de um contexto reativo. */
function setSearchChip( ctx, term ) {
	if ( ! ctx || ! Array.isArray( ctx.activeFilters ) ) {
		return;
	}
	const others = ctx.activeFilters.filter( function ( f ) {
		return f.type !== SEARCH_TYPE;
	} );
	if ( term ) {
		others.push( {
			type: SEARCH_TYPE,
			value: term,
			activeLabel: 'Nome: ' + term,
		} );
	}
	// Reatribuição dispara a reatividade → chips (data-wp-each) re-renderizam.
	ctx.activeFilters = others;
}

// Extensão ADITIVA do store do WooCommerce (nunca sobrescreve chaves do WC).
store( 'woocommerce/product-filters', {
	actions: {
		// Digitação no campo de busca.
		amSearchInput( event ) {
			const ctx = getContext();
			stashedContext = ctx;
			const term = event.target.value.trim();

			// Atualiza o chip imediatamente (feedback instantâneo, sem esperar a rede).
			setSearchChip( ctx, term );

			// A navegação (que aplica o filtro na grade) é debounced.
			clearTimeout( debounceTimer );
			debounceTimer = setTimeout( function () {
				routerNavigate( buildUrl( term ).href );
			}, DEBOUNCE_MS );
		},

		// Enter dispara a busca imediatamente.
		amSearchKeydown( event ) {
			if ( event.key !== 'Enter' ) {
				return;
			}
			event.preventDefault();
			const ctx = getContext();
			stashedContext = ctx;
			const term = event.target.value.trim();
			setSearchChip( ctx, term );
			clearTimeout( debounceTimer );
			routerNavigate( buildUrl( term ).href );
		},
	},
	callbacks: {
		// data-wp-init no wrapper de busca: guarda o contexto reativo assim que
		// o bloco é montado (inclusive após navegação), para a remoção do chip.
		amStashContext() {
			stashedContext = getContext();
		},
	},
} );

// Remoção do chip "Nome: …" em Filtros ativos. O botão nativo dispara
// actions.removeActiveFilter, cujo navigate() reconstrói a URL a partir da
// canonicalUrl — que AINDA contém filter_nome (o WC não reconhece esse
// parâmetro), então a busca não sairia da query. Capturamos o clique ANTES
// (fase de captura) e assumimos a remoção — só quando o item é o NOSSO
// (type === 'am-search'). Qualquer outro chip segue 100% pelo fluxo nativo.
document.addEventListener(
	'click',
	function ( e ) {
		const btn = e.target && e.target.closest ? e.target.closest( CHIP_REMOVE_SELECTOR ) : null;
		if ( ! btn ) {
			return;
		}
		const ctxAttr = btn.getAttribute( 'data-wp-context' );
		if ( ! ctxAttr ) {
			return;
		}
		let parsed;
		try {
			parsed = JSON.parse( ctxAttr );
		} catch ( err ) {
			return;
		}
		if ( ! parsed || ! parsed.item || parsed.item.type !== SEARCH_TYPE ) {
			return;
		}

		e.stopImmediatePropagation();
		e.preventDefault();

		// Remove o chip do estado client-side (some na hora) e navega sem filter_nome.
		setSearchChip( stashedContext, '' );
		routerNavigate( buildUrl( '' ).href );
	},
	true // captura — roda antes do handler nativo do WooCommerce
);
