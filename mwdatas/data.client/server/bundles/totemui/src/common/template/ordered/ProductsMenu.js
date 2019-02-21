import React, { Component } from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import ReactLoading from 'react-loading'
import ProductImg from '../../images/img_hamburguer.png'
import Grid from '../../layout/grid'
import SaleOptionsModal from '../components/SaleOptionsModal'
import { changeScreenAction, changeSubScreenAction, changeCouponAction, changeTextTop, productSaleOptionsAction, cleanSaleOptions, registerProductAction, alterUrlTopAction, expandedFooterAction, errorAction } from '../../../actions'
import { COUPON_KEYBOARD, BASE_URL, PRODUCT_SCREEN } from '../../../common/constants'

const buttonStyle = {
	color: '#3a1b0a'
}

export class ProductsMenu extends Component {
	constructor(props) {
		super(props)
		this.state = {
			modalOption: false,
			modalOptionSelected: null,
			scrollClass: "hide-scroll",
		}
	}

	registreProduct(product) {
		this.props.registerProductAction(product.partCode, 1, false, product.size).then((result)=>{
			if (((result.payload || {}).request || {}).status >= 300) {
				this.props.errorAction(result.payload)
			}
		})
		this.props.changeSubScreenAction(PRODUCT_SCREEN)
		this.props.expandedFooterAction(false)
		this.handleCloseModal()
	}

	handleProductClick(button) {
		this.props.changeCouponAction(null)
		this.props.productSaleOptionsAction(button.productCode).then((data) => {
			const optList = data.payload.data
			if (optList.length == 1) {
				this.registreProduct(optList[0])
			} else {
				const defaultProd = optList[0].size ? _.find(optList, {partCode: button.productCode}) : null
				this.setState({ modalOption: true, modalOptionSelected: defaultProd })
			}
		})
	}

	handleModalOptionClick = (modalOptionSelected) => {
		this.setState({
			modalOptionSelected
		})
	}

	handleCloseModal = () => {
		this.props.cleanSaleOptions()
		this.setState({
			modalOptionSelected
			: null, modalOption: false
		})
	}

	handleConfirmModal = () => {
		if (this.state.modalOptionSelected) {
			this.registreProduct(this.state.modalOptionSelected)
		} else {
			this.registreProduct(this.props.product.allOptions.data[0])
		}
	}

	renderProductButtons() {
		if (((this.props.selectedSideMenu || {}).name || "").toLowerCase().match(/promo*/)) {
			return (
				<div className="text-center">
                    <div className="text-header font-index font-inicio font-msg-promo">
                        <p style={{ color: '#eeaa03' }}>Cupons e descontos</p>
                        <p style={{ color: '#3a1b0a' }}>temporariamente disponíveis</p>
                        <p style={{ color: '#3a1b0a' }}>somente no balcão</p>
                    </div>
                </div>
			)
		}
		if ((this.props.product || {}).allProducts === 'void') {
			return (
				<div className="text-center">
                    <div className="text-header font-index font-inicio font-msg-promo">
                        <p style={{ color: '#eeaa03' }}>ITENS</p>
                        <p style={{ color: '#eeaa03' }}>TEMPORARIAMENTE</p>
                        <p style={{ color: '#eeaa03' }}>INDISPONÍVEIS</p>
                    </div>
                </div>
			)
		}
		if (!this.props.product || !this.props.product.allProducts || this.props.product.allProducts.length === 0) {
			return (<ReactLoading type="spin" color="#444" />)
		}
		return _.map(this.props.product.allProducts, (button, index) => {
			const name = ((new DOMParser().parseFromString((button.localizedName || "").toLowerCase(), "text/html")).documentElement.textContent).toUpperCase()
			return (
				<div key={index} className="bg-produto text-center" onClick={() => this.handleProductClick(button)}>
					<div style={{ width: "120px", height: "120px", display: "block", margin: "auto", position: "relative" }}>
						<img src={BASE_URL + button.imageUrl} className="width-produto" alt="bg" />
					</div>
					<div className="font-index" style={buttonStyle}>
						<p className="titulo-produto produto-nome-king" dangerouslySetInnerHTML={{__html: name}} />
					</div>
				</div>
			)
		});
	}

	handleIncludeCouponClick() {
		this.props.changeScreenAction(COUPON_KEYBOARD)
		this.props.changeTextTop(this.props.strings.TYPE_COUPON_CODE)
	}

	handleScroll = (event) => {
		if (this.scrollTimeout) {
			clearTimeout(this.scrollTimeout)
		}
		this.setState({scrollClass: "show-scroll"})

		this.scrollTimeout = setTimeout(this.hideScroll, 1000)
		console.log('handle scroll called')
	}
	hideScroll = () => {
		console.log("hide scroll called")
		this.setState({scrollClass: "hide-scroll"})
		clearTimeout(this.scrollTimeout)
		this.scrollTimeout = null
	}

	componentWillUnmount() {
		if (this.scrollTimeout) {
			clearTimeout(this.scrollTimeout)
		}
	}


	render() {
		if (this.state.error) {
			return <ModalError />
		}
		return (
			<div>
				<div ref={(el)=>this.scrollElement = el} className={`col-sm-9 col-md-9 rolagem ${this.state.scrollClass}`} style={{ paddingLeft: 0, width: '72%'}} onScroll={this.handleScroll}>
					<div className="col-sm-12 col-md-12 produtos" style={{padding: 0}}>
						{this.props.selectedSideMenu && !this.props.selectedSideMenu.name.toLowerCase().match(/promo*/) && this.props.selectedSideMenu.isPromo == '1' &&
							<div onClick={() => this.handleIncludeCouponClick()}>
								<Grid cols='12 12 12' className="div-btns-resumo-cupom" >
									<Grid cols='6 6 6' className="text-left" >
										<div className="btn-cupom  text-btn-resumo">{this.props.strings.CHOOSE_COUPON}</div>
									</Grid>
								</Grid>
							</div>
						}
						{(this.props.selectedSideMenu || {}).isPromo !== '1' && this.renderProductButtons()}

					</div>
				</div>
				<SaleOptionsModal
					show={this.state.modalOption}
					options={this.props.product.allOptions.data}
					selected={this.state.modalOptionSelected}
					onOptionClick={this.handleModalOptionClick}
					onClose={this.handleCloseModal}
					onConfirm={this.handleConfirmModal}
				/>
			</div>
		)
	}
}

function mapStateToProps(state) {
	return {
		order: state.order,
		selectedSideMenu: state.selectedSideMenu,
		strings: state.strings,
		product: state.product,
	}
}

function mapDispatchToProps(dispatch) {
	return bindActionCreators({
		changeTextTop,
		productSaleOptionsAction,
		alterUrlTopAction,
		changeScreenAction,
		changeSubScreenAction,
		cleanSaleOptions,
		registerProductAction,
		expandedFooterAction,
		changeCouponAction,
		errorAction
	}, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(ProductsMenu)