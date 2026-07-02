<?php
/**
 * REFERÊNCIA — Filtro customizado no Product Filters do WooCommerce (AJAX).
 *
 * Extrato das partes relevantes de wp-content/themes/arabian-mirage/inc/loja-blocos.php.
 * Exemplo: busca por NOME (param `filter_nome`, chip type `am-search`, bloco
 * `arabian-mirage/product-filter-search`). Troque os nomes para o seu filtro.
 *
 * NÃO estende classes do WooCommerce. Usa só APIs públicas (hooks + Block API).
 *
 * @package arabian-mirage
 */

defined( 'ABSPATH' ) || exit;

/* ============================================================================
 * 0. ENQUEUE — o JS DEVE ser SCRIPT MODULE (não wp_enqueue_script clássico).
 *    Só assim o import map resolve @wordpress/interactivity-router e a navegação
 *    acontece sem reload. Escopado aos archives da loja.
 * ========================================================================== */
add_action(
	'wp_enqueue_scripts',
	function () {
		$is_loja_archive = ( function_exists( 'is_shop' ) && is_shop() )
			|| ( function_exists( 'is_product_taxonomy' ) && is_product_taxonomy() );
		if ( ! $is_loja_archive ) {
			return;
		}
		$dir = get_stylesheet_directory();
		$uri = get_stylesheet_directory_uri();

		$js_module = $dir . '/assets/loja-search.js';
		if ( file_exists( $js_module ) && function_exists( 'wp_enqueue_script_module' ) ) {
			wp_enqueue_script_module(
				'am-loja-search',
				$uri . '/assets/loja-search.js',
				array( '@wordpress/interactivity', '@wordpress/interactivity-router' ),
				(string) filemtime( $js_module )
			);
		}
	},
	20
);

/* ============================================================================
 * 1. QUERY — query var própria + aplicação na query principal.
 *    NUNCA use o `s` nativo (marca a página como busca e força reload).
 * ========================================================================== */

/** Lê o termo da URL, sanitizado. */
function am_get_search_filter_term() {
	// phpcs:ignore WordPress.Security.NonceVerification.Recommended
	return isset( $_GET['filter_nome'] ) ? sanitize_text_field( wp_unslash( $_GET['filter_nome'] ) ) : '';
}

add_filter(
	'query_vars',
	function ( $vars ) {
		$vars[] = 'filter_nome';
		return $vars;
	}
);

add_action(
	'woocommerce_product_query',
	function ( $query ) {
		if ( is_admin() || ! $query->is_main_query() ) {
			return;
		}
		$is_loja_archive = ( function_exists( 'is_shop' ) && is_shop() )
			|| ( function_exists( 'is_product_taxonomy' ) && is_product_taxonomy() );
		if ( ! $is_loja_archive ) {
			return;
		}
		$term = am_get_search_filter_term();
		if ( '' !== $term ) {
			// Para busca textual usamos `s`; para outros filtros custom, use
			// meta_query/tax_query conforme o critério.
			$query->set( 's', $term );
		}
	}
);

/* ============================================================================
 * 2. CHIP — registra o item em "Filtros ativos" pelo hook PÚBLICO que todos os
 *    filtros nativos usam. Type de namespace próprio p/ nunca colidir.
 * ========================================================================== */
add_filter(
	'woocommerce_blocks_product_filters_selected_items',
	function ( $items ) {
		$term = am_get_search_filter_term();
		if ( '' === $term ) {
			return $items;
		}
		$items[] = array(
			'type'        => 'am-search', // namespace próprio (não price/status/rating/attribute/taxonomy)
			'value'       => $term,
			/* translators: %s: termo pesquisado. */
			'activeLabel' => sprintf( __( 'Nome: %s', 'arabian-mirage' ), $term ),
		);
		return $items;
	}
);

/* ============================================================================
 * 3. BLOCO — controle próprio do tema, COM diretivas da Interactivity API.
 *    O namespace `woocommerce/product-filters` é herdado do wrapper nativo
 *    (este bloco é renderizado dentro dele no template part).
 * ========================================================================== */
add_action(
	'init',
	function () {
		if ( ! function_exists( 'register_block_type' ) ) {
			return;
		}
		register_block_type(
			'arabian-mirage/product-filter-search',
			array(
				'api_version'     => 3,
				'render_callback' => 'am_render_product_filter_search',
				'supports'        => array( 'interactivity' => array( 'clientNavigation' => true ) ),
			)
		);
	}
);

/**
 * HTML do controle. Diretivas:
 *  - data-wp-init  → guarda o contexto reativo (p/ remoção do chip fora de escopo)
 *  - data-wp-on--input / --keydown → disparam a busca AJAX (actions do store estendido)
 */
function am_render_product_filter_search() {
	$term = am_get_search_filter_term();
	ob_start();
	?>
	<div
		class="am-filter am-filter--search is-open"
		data-am-filter-label="Nome do Produto"
		data-wp-init="callbacks.amStashContext"
	>
		<div class="am-filter__header">
			<h3 class="am-filter__title">Nome do Produto</h3>
		</div>
		<div class="am-search-field">
			<input
				type="search"
				class="am-search-field__input"
				placeholder="Buscar por nome..."
				aria-label="<?php esc_attr_e( 'Buscar produto por nome', 'arabian-mirage' ); ?>"
				value="<?php echo esc_attr( $term ); ?>"
				data-wp-on--input="actions.amSearchInput"
				data-wp-on--keydown="actions.amSearchKeydown"
			/>
		</div>
	</div>
	<?php
	return ob_get_clean();
}
