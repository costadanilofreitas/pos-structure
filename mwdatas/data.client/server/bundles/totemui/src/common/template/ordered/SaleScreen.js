import React, { Component } from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import SideMenu from './SideMenu'
import OnSale from './onSale'
import ProductsMenu from './ProductsMenu'
import Top from './top'
// import { ON_SALE_SCREEN, SALE_SCREEN } from '../../constants'
import { changeScreenAction, showSuggestionAction } from '../../../actions'

export class SaleScreen extends Component {

	// renderSelectedScreen = () => {
	// 	switch (this.props.selectedSideMenu) {
	// 		case ON_SALE_SCREEN:
	// 			return <OnSale />
	// 		default:
	// 			return <ProductsMenu />
	// 	}
	// }

	componentWillMount = () => {
		this.props.showSuggestionAction(true)
	}

	render() {
		return (
			<div>
				<Top cancelOrder={true} />
				<SideMenu />
				{/* {this.renderSelectedScreen()} */}
				<ProductsMenu />
			</div>
		)
	}
}

function mapStateToProps(state) {
	return {
		selectedScreen: state.selectedScreen,
		// selectedSideMenu: state.selectedSideMenu
	}
}

function mapDispatchToProps(dispatch) {
	return bindActionCreators({
		changeScreenAction,
		showSuggestionAction
	}, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(SaleScreen)
