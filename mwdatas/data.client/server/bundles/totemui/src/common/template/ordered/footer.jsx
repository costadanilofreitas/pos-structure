import React, { Component } from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { DINE_IN, TAKE_OUT, PAYMENT_SCREEN, NAME_SCREEN, MAIN_SCREEN, BASE_URL, PRODUCT_SCREEN } from '../../constants'
import { saleCancelAction, changeSubScreenAction, changeScreenAction, changeTextTop, saleAddItemAction, saleRemoveItemAction, changeProductAction, expandedFooterAction } from '../../../actions'
import OrderItems, { OrderItems as OrderItem } from './orderItems'
import ModalCpf from '../../msg/modalCpf'
import Modal from '../../msg/modal'
import ImgBtnUp from '../../../common/images/icon_up.png'
import ImgBtnDown from '../../../common/images/icon_down.png'
import _ from 'lodash'

const textStyle = {
	color: "#3a1b0a"
}

var valorTotal = 0

export class Footer extends Component {
	constructor(props) {
		super(props);
		this.state = {
			cancelAlert: false,
			cpfModal: false,
			showChangeModal: false,
			modalData: null,
			modalRepeatAmount: 1
		};
	}

	componentDidMount() {

		if (this.props.selectedScreen === PAYMENT_SCREEN && !this.props.order.expandedFooter) {
			this.props.expandedFooterAction(true)
			this.setState({ modalRepeatAmount: 1 });
		}
	}
	canToggle() {
		return this.props.order.items.length > 0 && this.props.selectedScreen != PAYMENT_SCREEN
	}
	handleToggleExpand = () => {

		if (this.canToggle()) {
			this.props.expandedFooterAction(!this.props.order.expandedFooter)
		}

	}

	handleFinishOrder = () => {
		if (this.props.selectedScreen === PAYMENT_SCREEN) {
			this.setState({ cpfModal: true })
		} else {
			this.props.changeSubScreenAction(MAIN_SCREEN)
			this.props.changeScreenAction(PAYMENT_SCREEN)
			this.props.changeTextTop(this.props.strings.ORDER_HEADER)
		}
	}

	handleCancelOrder = () => {
		this.setState({ cancelAlert: true })
	}

	renderLocalText = () => {
		switch (this.props.order.type) {
			case DINE_IN:
				return this.props.strings.EAT_IN_FOOTER_TEXT
			case TAKE_OUT:
				return this.props.strings.TAKE_OUT_FOOTER_TEXT
		}
	}

	handleItemClick = (modalData) => {
		this.setState({ showChangeModal: true, modalData })
	}

	renderSelectedScreen = () => {
		switch (this.props.selectedScreen) {
			case PAYMENT_SCREEN:
				return null
			default:
				return <OrderItems onItemClick={this.handleItemClick} />
		}
	}

	handleModal = () => {
		if (this.state.cancelAlert) {
			return <Modal
				showModal={true}
				onClose={this.handleCloseModal}
				divCenter={this.props.strings.CANCEL_ORDER_CONFIRM}
				onConfirm={this.handleConfirmCancelOrder}
				onCancel={this.handleCloseModal}
				okButtonText={this.props.strings.YES}
				cancelButtonText={this.props.strings.NO} showCancel
			/>
		} else if (this.state.cpfModal){
			return <ModalCpf showModal={true} />
		}
	}

	handleAddRepeatProduct = (amount) => {
		this.setState({ modalRepeatAmount: Math.min(Math.max(this.state.modalRepeatAmount + amount, 1), 9) })
	}
	handleCloseModal = () => {
		this.setState({ cancelAlert: false })
	}

	handleCloseChangeModal = () => {
		this.setState({ showChangeModal: false })
	}

	handleRepeat = () => {
		const newItem = _.cloneDeep(this.state.modalData)
		delete newItem.line
		for (let i = 0; i < this.state.modalRepeatAmount; i++) {
			this.props.saleAddItemAction(this.props.order.sale_token, _.cloneDeep(newItem))
		}

		this.setState({ modalRepeatAmount: 1 });
		this.handleCloseChangeModal()
	}

	handleRemoveItem = () => {
		this.props.saleRemoveItemAction(this.props.order.sale_token, this.state.modalData.line)
		this.handleCloseChangeModal()
		if (this.props.order.items.length === 1) {
			this.props.expandedFooterAction(false)
		}
	}

	handleChangeItem = () => {
		const newData = _.cloneDeep(this.state.modalData)
		function cleanupItem(item) {
			delete item.custom
			delete item.selected
			if (item && item.pendent === false){
				item.pendent = true
			}
			_.forEach(item.sons, (son) => cleanupItem(son))
		}
		cleanupItem(newData)
		this.props.changeProductAction(newData)
		this.props.changeSubScreenAction(PRODUCT_SCREEN)
		this.handleCloseChangeModal()
		this.props.expandedFooterAction(false)
	}

	handleConfirmCancelOrder = () => {
        this.props.saleCancelAction(this.props.order.sale_token)
	}

	_calcTotalItem(product) {
		if (product.totalPrice) {
			valorTotal += Number(product.totalPrice) * Number(product.currentQuantity)
		}
	}

	calcTotal() {
		valorTotal = 0

		if (this.props.productCurrent && !_.isEqual(this.props.productCurrent, {})) {
			this._calcTotalItem(this.props.productCurrent)
		}

		_.map(this.props.order.items, (item) => {
			this._calcTotalItem(item)
		})

		return valorTotal.toLocaleString(this.props.strings.LOCALE, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
	}

	renderModal() {
		return (
			<div className="modal show" id="modalEditProduto" tabIndex="-1" role="dialog" data-backdrop="static" data-keyboard="false" aria-labelledby="myModalLabel" aria-hidden="true" style={{ backgroundColor: "rgba(100, 100, 100, 0.6)" }}>
				<div className="vertical-alignment-helper">
					<div className="modal-dialog vertical-align-center">
						<div id="bodyModal" className="modal-selecao modal-content-pedido">
							<div className="bg-modal">
								<div className="bg-modal-int-pedido">
									<div className="modal-header">
										<div className="max-width row">
											<div className="form-inline">
												<div className="col-sm-10 col-md-8 text-left">
													<h4 className="modal-title-pedido titulo-produto" ref={(node) => { if (node) { node.style.setProperty("fontSize", "298%", "important"); } }} style={{ color: "white" }}>O QUE VOCÊ DESEJA MUDAR?</h4>
												</div>
												<div className="col-sm-2 col-md-4">
													<div className="close close-modal-pedido" onClick={() => this.handleCloseChangeModal()}></div>
												</div>

											</div>
										</div>
									</div>
									<div className="modal-body modal-pedido-pedd" style={{ padding: 0, maxHeight: 180}}>
										<div className="row" style={{ marginTop: "30px", height: 130 }}>
											<div id="prod-1" className="text-center change-prod-button" onClick={this.handleChangeItem}>
												<div style={{ width: "120px", height: "120px", display: "block", margin: "auto", position: "relative" }}>
													<img src={`${BASE_URL}${this.state.modalData.imageUrl}`} alt="bg" className="width-produto" />
												</div>
												<div className="font-produto" style={{ color: "#3a1b0a" }}>
													<p className="font-produto produto-nome-king">{`${this.state.modalData.localizedName}`}</p>
												</div>
											</div>
											<div className="item-preview-build">
												<OrderItem scroll={true} order={{items: [this.state.modalData]}} strings={this.props.strings} />
											</div>
										</div>
										<div className="row" style={{ marginTop: 75, marginLeft: 15 }}>
											<div className="col-sm-4 col-md-4">
												<div className="btn-modal-cancel-include font-btn-pedido" onClick={() => this.handleCloseChangeModal()}>
													<span className="font-index text-btn-cancel-modal-include" style={{ marginLeft: 0, padding: 0 }} >CANCELAR</span>
												</div>
											</div>
											<div className="col-sm-4 col-md-4">
												<div className="btn-modal-cancel-include font-btn-pedido" onClick={this.handleRemoveItem}>
													<span className="font-index text-btn-cancel-modal-include" style={{ marginLeft: 0, padding: 0 }} >REMOVER</span>
												</div>
											</div>
											<div className="col-sm-4 col-md-4">
												<div className="btn-modal-edit-include font-btn-pedido" onClick={this.handleChangeItem}>
													<span className="font-index text-btn-modal-itensExtras" style={{ padding: 0, marginLeft: 0, position: 'initial' }} >EDITAR</span>
												</div>
											</div>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div >
		)
	}

	render() {
		return (
			<footer>
				<div className="max-width">
					{this.canToggle() && this.props.order.expandedFooter && <div onClick={this.handleToggleExpand} style={{ width: '100%', height: '100%', top: 0, position: 'fixed', backgroundColor: 'rgba(100,100,100,0.5)', zIndex: -1 }}></div>}
					<div className={`row no-margin-bottom resumo-pedido ${this.props.order.expandedFooter ? 'footer-shadow-open' : 'footer-shadow-close'}`} onClick={this.handleToggleExpand} >
						<div className="col-sm-7 col-md-7 text-left" style={{ marginTop: "24px" }}>
                            {this.canToggle() && <img src={this.props.order.expandedFooter ? ImgBtnDown : ImgBtnUp} className="icon_voltar" alt="voltar" style={{ marginRight: '10px', marginTop: '-12px', width: 30 }} />}
							<span id="local" className="font-index rodape" style={textStyle}>{this.renderLocalText()}</span>
						</div>
						<div className="col-sm-5 col-md-5 text-right">
							<p className="font-index rodape-preco" style={textStyle}>{this.props.strings.TOTAL}: <span style={{ color: 'white' }}>R$ <span id="valorCarrinho">{this.calcTotal()}</span> </span>
							</p>
						</div>
					</div>
					<div id="detalhePedido" className={`row no-margin-bottom  ${this.props.order.expandedFooter ? 'resumo-pedido-open' : 'resumo-pedido-close'} ${(this.props.selectedScreen === PAYMENT_SCREEN) ? 'resumo-pedido-open-fluxo' : ''}`}>

						<div className="col-sm-12 col-md-12 text-left">
							{this.renderSelectedScreen()}
						</div>

						<div className={`col-sm-12 col-md-12  div-btns-resumo ${(this.props.selectedScreen === PAYMENT_SCREEN) ? '' : 'div-btns-resumo-order'}`}>
							<div className="row">
								<div className={"col-sm-6 col-md-6 text-left"}>
									<div className="btn-cancelar-pedido text-center" onClick={this.handleCancelOrder}>
										<span className="text-btn-resumo">{this.props.strings.CANCEL_ORDER}</span>
									</div>
								</div>
								<div className="col-sm-6 col-md-6 text-left">
									<div className="btn-finalizar-pedido text-center" onClick={this.handleFinishOrder}>
										<span className="text-btn-resumo">{this.props.strings.CONFIRM_ORDER}</span>
									</div>
								</div>
							</div>
						</div>
					</div>

					{this.handleModal()}

				</div>
				{this.state.showChangeModal ? this.renderModal() : null}
			</footer>
		)
	}
}

function mapStateToProps(state) {
	return {
		order: state.order,
		productCurrent: state.product.productCurrent,
		selectedScreen: state.selectedScreen,
		modalState: state.modalState,
		strings: state.strings,
		acumulateValue: state.acumulateValue
	}
}

function mapDispatchToProps(dispatch) {
	return bindActionCreators({
		changeScreenAction,
		changeSubScreenAction,
		changeTextTop,
		saleAddItemAction,
		saleRemoveItemAction,
		changeProductAction,
		expandedFooterAction,
		saleCancelAction
	}, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(Footer)