import React, { Component } from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import _ from 'lodash'
import ReactLoading from 'react-loading'
import Top from './top'
import { changeScreenAction, changeSubScreenAction, registerProductAction, changeTextTop, expandedFooterAction, setCouponDataAction } from '../../../actions'
import { MAIN_SCREEN, BASE_URL, PRODUCT_SCREEN, SALE_SCREEN, COUPON_KEYBOARD } from '../../../common/constants'
import imgCircle from '../../../common/images/circle.png'

const buttonStyle = { color: '#3a1b0a' }

export class CouponOptionScreen extends Component {
	constructor(props) {
		super(props)
		this.state = {
		}
	}

	handleButtonClick(selectedItemModal) {
		this.props.registerProductAction(selectedItemModal.productCode)
		this.props.changeSubScreenAction(PRODUCT_SCREEN)
		this.props.expandedFooterAction(false)
	}

	renderButtons() {
		return _.map(this.props.couponData, (button, idx) => {
			return (
				<div key={idx} className="produto-combo text-center" onClick={() => this.handleButtonClick(button)}>
					<div style={{ width: "120px", height: "120px", display: "block", margin: "auto", position: "relative" }}>
						<img src={BASE_URL + button.imageUrl} alt="bg" className="width-produto" />
					</div>
					<div className="font-index" style={buttonStyle}>
						<p className="titulo-produto produtos-nome-fries">{button.localizedName}</p>
					</div>
				</div>
			)
		})
	}

	handlerGoBack() {
		this.props.changeTextTop(this.props.strings.CHOOSE_HERE)
		this.props.changeScreenAction(COUPON_KEYBOARD)
		this.props.changeSubScreenAction(MAIN_SCREEN)
	}


	render() {
		return (
			<div>
				<Top onGoBack={() => this.handlerGoBack()} />
				<div className="row rolagem">
					<span className="titulo-combo">ESCOLHA SUA OPÇÃO</span>
					<div className="col-sm-12 col-md-12 produtos-combo rolagem">
						{this.renderButtons()}
					</div>
				</div>
			</div>
		)
	}
}

function mapStateToProps(state) {
	return {
		couponData: state.couponData,
		strings: state.strings
	}
}

function mapDispatchToProps(dispatch) {
	return bindActionCreators({
		changeScreenAction,
		changeSubScreenAction,
		registerProductAction,
		changeTextTop,
		expandedFooterAction,
		setCouponDataAction
	}, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(CouponOptionScreen)