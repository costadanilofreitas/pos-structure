import React, { Component } from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import _ from 'lodash'
import ReactLoading from 'react-loading'
import Top from './top'
import { changeSubScreenAction, registerProductAction, alterProductAction, changeTextTop, showSuggestionAction, expandedFooterAction } from '../../../actions'
import { MAIN_SCREEN, BASE_URL, PRODUCT_SCREEN, SALE_SCREEN } from '../../../common/constants'
import imgCircle from '../../../common/images/circle.png'

const buttonStyle = { color: '#3a1b0a' }

export class SuggestionScreen extends Component {
	constructor(props) {
		super(props)
		this.state = {
			// selectedItemsAmount: [0, 0, 0, 0, 0, 0],
			selectedItemModal: null,
			// modalPendingAmount: 1,
			showModal: false,
		}
	}

	componentWillMount = () => {
		this.props.showSuggestionAction(false)
	}

	handleButtonClick(selectedItemModal) {
		if (selectedItemModal.currentyQuantity == 1) {
			selectedItemModal.currentyQuantity = 0
		} else {
			selectedItemModal.currentyQuantity = 1
		}

		this.setState({
			selectedItemModal,
		})
	}

	renderButtons() {
		return _.map(this.props.allProductsSuggested.data, (button, idx) => {
			return (
				<div key={idx} className="produto-combo text-center" onClick={() => this.handleButtonClick(button)}>
					<div style={{ width: "120px", height: "120px", display: "block", margin: "auto", position: "relative" }}>
						<img src={BASE_URL + button.product.imageUrl} alt="bg" className="width-produto" />
					</div>
					{
						button.currentyQuantity > 0 ?
							<span>
								<img src={imgCircle} className="circle-selecao" alt="bg" />
								<span className="font-index font-contador-itens">{_.padStart(button.currentyQuantity, 2, '0')}</span>
							</span>
							: null
					}
					<div className="font-index" style={buttonStyle}>
						<p className="titulo-produto produtos-nome-fries">{button.product.part.localizedName}</p>
					</div>
				</div>
			)
		})
	}

	handleCancel() {
		this.props.changeSubScreenAction(MAIN_SCREEN)
		this.props.changeTextTop(this.props.strings.CHOOSE_HERE)
		this.props.expandedFooterAction(true)
	}

	handleConfirm() {
		this.props.alterProductAction([]) //Limpar lista produtos atuais

		var listsuggestions = this.props.allProductsSuggested.data.filter((sug) => {
			return sug.currentyQuantity > 0
		})

		if (listsuggestions.length == 0) {
			this.handleCancel()
		} else {

			_.each(listsuggestions, (prod, index) => {
				this.props.registerProductAction(prod.product.productCode, prod.currentyQuantity, true).then(() => {
					if ((index + 1) == listsuggestions.length) {
						setTimeout(() => {
							this.props.changeSubScreenAction(PRODUCT_SCREEN)
						}, 100);
					}
				})
			})
		}
	}

	handleAdd(amount) {
		let selectedItemModal = this.state.selectedItemModal
		selectedItemModal.currentyQuantity = Math.max(0, Number(selectedItemModal.currentyQuantity) + amount)

		this.setState({ selectedItemModal })
	}

	handleCloseModal(apply) {
		this.setState({ showModal: false })
	}

	renderModal() {
		if (!this.state.showModal) {
			return null
		}

		return (
			<div className="modal show" tabIndex="-1" role="dialog" id="modalSugestion" data-backdrop="static" data-keyboard="false" aria-labelledby="myModalLabel" style={{ backgroundColor: "rgba(100,100,100,0.6)" }}>
				<div className="vertical-alignment-helper">
					<div className="modal-dialog vertical-align-center">
						<div className="modal-selecao modal-content">
							<div className="bg-modal">
								<div className="bg-modal-int">
									<div className="modal-header">
										<div className="max-width row" style={{ marginBottom: 0 }}>
											<div className="form-inline">
												<div className="col-sm-10 col-md-8 text-left">
													<h4 className="modal-title-itensExtras titulo-produto">{this.props.strings.CHOOSE_AMOUNT}</h4>
												</div>
												<div className="col-sm-2 col-md-4">
													<div className="close close-modal" onClick={() => this.handleCloseModal(false)}></div>
												</div>
											</div>
										</div>
									</div>
									<div className="modal-body">
										<div className="max-width row-produto-modal">
											<div className="row body-modal-itensExtras">
												<div className="col-md-2 col-sm-2 padding-top-button-modal">
													<div className="menos-modal-itensExtras" onClick={() => this.handleAdd(-1)}>
													</div>
												</div>
												<div className="col-md-8 col-sm-8" style={{ textAlign: "center", pointerEvents: "none" }}>
													<img src={BASE_URL + this.state.selectedItemModal.product.imageUrl} className="img-modal-itensExtras" style={{ position: "inherit" }} alt="bg" />
												</div>
												<div className="col-md-2 col-sm-2 padding-top-button-modal">
													<div className="mais-modal-itensExtras" onClick={() => this.handleAdd(+1)}>
													</div>
												</div>
											</div>

										</div>
										<div className="row body-modal-itensExtras">

											<div className="col-md-12 col-sm-12">
												<div className="font-index font-img-modal-itensExtras">
													<p className="titulo-produto produtos-nome-fries">{this.state.selectedItemModal.product.part.localizedName}</p>
													<p className="font-contador-modal-itensExtras"><span>{this.state.selectedItemModal.currentyQuantity}</span></p>
												</div>
											</div>

										</div>
										<div className="max-width">
											<div className="col-sm-6 col-md-6 btn-modal-itensExtras-text">
												<div className="btn-modal-itensExtras-ok" onClick={() => this.handleCloseModal(true)}>
													<span className="font-index text-btn-modal-itensExtras">{this.props.strings.CONFIRM}</span>
												</div>
											</div>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		)
	}

	existeSelected() {
		for (var index = 0; index < this.props.allProductsSuggested.data.length; index++) {
			if (this.props.allProductsSuggested.data[index].currentyQuantity > 0) {
				return true
			}
		}
		return false
	}

	handlerGoBack() {
		this.props.changeTextTop(this.props.strings.CHOOSE_HERE)
		this.props.changeSubScreenAction(MAIN_SCREEN)
	}


	render() {
		if (!this.props.allProductsSuggested || this.props.allProductsSuggested.length === 0) {
			return (<ReactLoading type="spin" color="#444" />)
		}

		if (!this.props.allProductsSuggested.data) {
			return (<div>Error...</div>)
		}


		return (
			<div>
				<Top onGoBack={() => this.handleCancel()} />
				<div className="row rolagem">
					<span className="titulo-combo">{this.props.strings.SUGGESTION_QUESTION}</span>
					<div className="col-sm-12 col-md-12 produtos-combo rolagem">
						{this.renderButtons()}
						<div className="col-sm-12 col-md-12 div-btns-resumo" style={{padding: 0, marginBottom: 0}}>
							<div className="row">
								<div className="col-sm-6 col-md-6 text-left">
									<div className="btn-cancelar-item text-center" onClick={() => this.handleCancel()}>
										<span className="font-index">{this.props.strings.CANCEL_SUGGESTION}</span>
									</div>
								</div>
								{
									this.existeSelected() &&
									<div className="col-sm-6 col-md-6 text-left">
										<div className="btn-finalizar-item text-center" onClick={() => this.handleConfirm()}>
											<span className="font-index">{this.props.strings.CONFIRM_SUGGESTION}</span>
										</div>
									</div>
								}

							</div>
						</div>
					</div>
				</div>
				{this.renderModal()}
			</div>
		)
	}
}

function mapStateToProps(state) {
	return {
		allProductsSuggested: state.product.allProductsSuggested,
		strings: state.strings,
		order: state.order
	}
}

function mapDispatchToProps(dispatch) {
	return bindActionCreators({
		changeSubScreenAction,
		registerProductAction,
		alterProductAction,
		changeTextTop,
		showSuggestionAction,
		expandedFooterAction
	}, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(SuggestionScreen)