import React, { Component } from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import ReactLoading from 'react-loading'
import _ from 'lodash'
import util from 'util'
import Footer from './footer'
import SideMenu from './SideMenu'
import ProductsMenu from './ProductsMenu'
import Top from './top'
import SaleOptionsModal from '../components/SaleOptionsModal'
import { productSaleOptionsAction, errorAction, changeSubScreenAction, alterProductAction, changeTextTop, saleSuggestedProductsAction, saleAddItemAction, alterUrlTopAction, expandedFooterAction } from '../../../actions'
import { MAIN_SCREEN, SUGGESTION_SCREEN, CUSTOMIZE_SCREEN, SALE_SCREEN, BASE_URL, COUPON_SCREEN } from '../../../common/constants'



const buttonStyle = {
	color: '#3a1b0a'
}

let break_ = false
let valorTotal = 0
let parts = []
let pendent = false
let back = true
let type = ""

export class ProductScreen extends Component {
	constructor(props) {
		super(props)
		this.state = {
			loading: false,
			modalOption: false,
			productsToChoose: null,
			modalOptionSelected: null,
		}
	}

	componentDidUpdate() {

		var element2 = this.productRolagem

		var element = document.getElementsByClassName("options");

		if (element && element.length > 2) {
			let newScroll = -380
			for (var index = 0; index < element.length - 1; index++) {
				newScroll += element[index].scrollHeight
			}

			setTimeout(() => {
				element2.scrollTop = newScroll
			}, 200)

		}
	}

	_calcTotalItem(product, zerarValorTotal) {
		if (zerarValorTotal)
			valorTotal = 0

		if (product.partType == 'Product') {
			valorTotal += Number(product.defaultQuantity) * Number(product.unitPrice)
			let dif = product.currentQuantity - product.defaultQuantity
			if (dif > 0) {
				valorTotal += dif * (Number(product.addedUnitPrice) + Number(product.unitPrice))
			}

			// valorTotal += Number(_.max([product.defaultQuantity, product.currentQuantity - product.defaultQuantity])) * Number((product.defaultQuantity == 0 && product.currentQuantity <= product.defaultQuantity) ? product.unitPrice : product.addedUnitPrice)
		}
		if (product.currentQuantity > 0) {
			_.map(product.sons, (prod) => {
				this._calcTotalItem(prod, false)
			})
		}
	}

	_calcTotal(newProduct) {
		this._calcTotalItem(newProduct, true)
		return valorTotal
	}

	_verifyPending(lstProductOriginal) {
		let pendentItem = false
		_.each(lstProductOriginal, (productOriginal) => {
			pendentItem = false

			if (productOriginal.partType == 'Product') {

				let op = productOriginal.sons[0]

				if (op && !op.selected && (op.custom != 'N') && op.partType == 'Option') {
					pendent = true;
					pendentItem = true
				}

			} else {
				_.map(productOriginal.sons, (option, index) => {
					if (option.partType == 'Option') {
						if (!option.selected && !option.ignore && option.minQuantity !== 0) {
							pendent = true;
							pendentItem = true
						}
					} else {
						_.map(option.sons, (optionProduct) => {
							if (option.cfh) {
								_.map(optionProduct.sons, (cfhOptions)=>{
									if (!cfhOptions.selected && (cfhOptions.custom != 'N') && cfhOptions.partType == 'Option'){
										pendent = true
										pendentItem = true
									}
								})
							} else if (!optionProduct.selected && (optionProduct.custom != 'N') && optionProduct.partType == 'Option') {
								pendent = true
								pendentItem = true
							}
						})
					}
				})
			}

			productOriginal.pendent = pendentItem
			productOriginal.totalPrice = this._calcTotal(productOriginal)
		})
	}

	productHasOption(product, option, parent = null) {
		if (parent &&
		    (
		    	(parent.partType === 'Option' && parent.minQuantity === 0 && product.currentQuantity === 0) ||
		    	(parent.partType === 'Combo') ||
		    	(product.partType === 'Combo')
		    ) &&
		    option.partCode === product.partCode) {
			return [parent, product]
		}
		for (let item of product.sons) {
			const ret = this.productHasOption(item, option, product)
			if (ret) {
				return ret
			}
		}
	}

	_save() {
		pendent = false
		let lstProductCurrent = this.props.productCurrent
		this._verifyPending(lstProductCurrent)

		if (pendent) { //ATUALIZAR REDUX
			this.props.alterProductAction([...lstProductCurrent])
		} else {
			this.setState({ loading: true })
			const lastItemSold = _.cloneDeep(this.props.order.items.slice(-1)[0])
			const pendingExtras = new Map();
			_.each(lstProductCurrent, (newProduct) => {
				// handle suggestion as promotional item
				if (this.props.oldSuggestion) {
					let optionToFill = this.productHasOption(lastItemSold, newProduct)
					if (optionToFill) {
						const [option, item] = optionToFill
						if (option.partType !== 'Combo') {
							option.currentQuantity = 1
							item.currentQuantity = 1
							lastItemSold.totalPrice = this._calcTotal(lastItemSold)
						} else {
							if (!pendingExtras.has(option)) {
								pendingExtras.set(option, [])
							}
							let found = false
							pendingExtras.forEach((_, option) => {
								if (found) {
									return
								}
								if (option.sons.find(opt=>opt.partCode === item.partCode)) {
									found = true
									pendingExtras.get(option).push(newProduct)
								}
							})
							if (found) {
								return
							}
						}
					}
				}
				this.props.saleAddItemAction(this.props.order.sale_token, newProduct).then((data) => {
					if (data.payload.message) {
						this.props.errorAction(data)
					} else if (this.props.productCurrent.length == 0) {
						if (this.props.showSuggestion) {
							this.renderSaleSuggestedProducts()
						} else {
							this.props.expandedFooterAction(true)
							this.props.changeTextTop(this.props.strings.CHOOSE_HERE)
							this.props.changeSubScreenAction(MAIN_SCREEN)
						}
					}
				})
			})
			pendingExtras.forEach((items, combo) => {
				if (items.length === combo.sons.length) {
					const optionToFind = this.productHasOption(lastItemSold, combo)
					if (optionToFind) {
						const option = optionToFind[0]
						option.currentQuantity = 1
						combo.currentQuantity = 1
						lastItemSold.totalPrice = this._calcTotal(lastItemSold)
						this.props.saleAddItemAction(this.props.order.sale_token, lastItemSold).then((data) => {
							if (data.payload.message) {
								this.props.errorAction(data)
							} else {
								this.props.expandedFooterAction(true)
								this.props.changeTextTop(this.props.strings.CHOOSE_HERE)
								this.props.changeSubScreenAction(MAIN_SCREEN)
							}
						})
					}
				} else {
					_.each(items, (item) => {
						item.totalPrice = this._calcTotal(item)
						this.props.saleAddItemAction(this.props.order.sale_token, item).then((data) => {
							if (data.payload.message) {
								this.props.errorAction(data)
							} else {
								this.props.expandedFooterAction(true)
								this.props.changeTextTop(this.props.strings.CHOOSE_HERE)
								this.props.changeSubScreenAction(MAIN_SCREEN)
							}
						})
					})
				}
			})
			this.setState({ loading: false })

		}
	}

	handlerConfirm(option) {
		option.currentQuantity = 1
		option.selected = 'Y'
		_.each(option.sons, (son)=> {
			if (son.currentQuantity === null) {
				son.currentQuantity = son.defaultQuantity
			}
		})
		this._save()
	}

	handlerCancel(option) {
		option.selected = 'N'
		this._save()
	}

	hasChanges = (item) => {
		if (item.partType === 'Product' &&
		  item.currentQuantity !== null &&
		  item.defaultQuantity !== null &&
		  item.currentQuantity !== item.defaultQuantity) {
			return true
		}
		return _.some(item.sons, this.hasChanges)
	}

	handlerOriginallyRecipe(prod) {
		delete prod.selected
		prod.currentQuantity = null
		_.map(prod.sons, (_option) => {
			_option.currentQuantity = null
			delete _option.selected
		})
		this.forceUpdate()
		this._save()
	}

	handlerQuantity(prod, numberSum, selected) {
		let totalCurrent = numberSum

		_.map(prod.sons, (p) => {
			if (p.currentQuantity === null) {
				p.currentQuantity = p.defaultQuantity
			}
			totalCurrent += p.currentQuantity
		})

		if (totalCurrent < prod.minQuantity) {
			console.log('NÃO PODE TER MENOS QUE ' + prod.minQuantity + ' OPÇÕES!')
			return null
		}

		if (totalCurrent > prod.maxQuantity) {
			console.log('NÃO PODE TER MAIS QUE ' + prod.maxQuantity + ' OPÇÕES!')
			return null
		}

		if (selected.currentQuantity === null) {
			selected.currentQuantity = selected.defaultQuantity
		}

		if ((selected.currentQuantity + numberSum) < selected.minQuantity) {
			console.log(selected.localizedName + ' NÃO PODE TER MENOS QUE ' + selected.minQuantity + ' INGREDIENTES!')
			return null
		}

		if ((selected.currentQuantity + numberSum) > selected.maxQuantity) {
			console.log(selected.localizedName + ' NÃO PODE TER MAIS QUE ' + selected.maxQuantity + ' INGREDIENTES!')
			return null
		}

		prod.currentQuantity = totalCurrent
		selected.currentQuantity += numberSum
		selected.selected = 'Y'
		this.forceUpdate()
		this._save()
	}

	_zerarOption(option) {
		option.sons = _.reduce(option.sons, (sons, op) => {
			if (!op.included) {
				// debugger
				op.currentQuantity = null
				delete op.selected
				this._zerarOption(op)
				sons.push(op)
			}
			return sons
		}, [])
	}
	handleConfirmOption(product, option=null) {
		option = option || this.state.selectedOptionProduct
		this._zerarOption(option)
		option.selected = 'Y'
		option.currentQuantity = 1
		product.currentQuantity = 1
		product.selected = 'Y'
		product.included = true
		option.sons.push(product)
		this.setState({modalOption: false})
		this._save()
	}
	handleClickOption(option, selected) {
		if (selected === -1) {
			//não incluir
			option.currentQuantity = 0
			option.selected = 'N'
			this._save()
		} else {
			this.props.productSaleOptionsAction(selected.partCode, option.partCode).then((data) => {
				if (data.payload.data.length == 1) {
					this.handleConfirmOption({...selected}, option)
				} else {
					const options = _.map(data.payload.data, (item) => {
						return {...selected, ...item, unitPrice: item.defaultPrice, partCode: item.partCode}
					})
					this.setState({ modalOption: true, selectedOptionProduct: option, productsToChoose: options, modalOptionSelected: options[1] })
				}
			})
		}
	}

	returnLabel(partCode, partCodeContext) {
		var lstLabel = this.props.optionLabels.data.filter((el) => {
			return el.partCode == partCode
		})

		if (lstLabel && lstLabel.length > 0) {
			return lstLabel[0]
		} else {
			return { localizedLabel: 'ESCOLHA', color: '#333' }
		}
	}

	renderSaleSuggestedProducts() {
		this.props.saleSuggestedProductsAction(this.props.order.sale_token, (this.props.selectedSideMenu || {}).id).then((response) => {
			if (((response.payload || {}).data || []).length > 0){
				this.props.changeSubScreenAction(SUGGESTION_SCREEN)
			} else {
				this.props.changeSubScreenAction(MAIN_SCREEN)
				this.props.changeTextTop(this.props.strings.CHOOSE_HERE)
				this.props.expandedFooterAction(true)
			}
		})
	}

	renderProduct(filho, label, type) {
		let opt = _.orderBy(filho.sons, 'defaultQuantity', 'desc')
		var html = (
			<div key={`${Math.random()}`}>
				<div className="max-width row center-body-custom">
					<div className="pnl-personaliza body-custom-snack rolagem show-scroll">
						{
							_.map(opt, (_option, index) => {
								return (
									<div key={`${Math.random()}`} className="row  item-personaliza">
										<div className="row pnl-item-personaliza" style={{ paddingTop: '5px' }}>
											<div className="col-sm-2 col-md-2 ">
												<div className="custom-buttons-counter menos-personaliza"
													onClick={() => this.handlerQuantity(filho, -1, _option)} ></div>
											</div>
											<div className="col-sm-6 col-md-6 text-center" style={{ paddingTop: '20px' }}>
												<span className="titulo-item-personaliza ">{_option.localizedName}</span>
											</div>
											<div className="col-sm-2 col-md-2 pull-rigth">
												<div className="custom-buttons-counter mais-personaliza"
													onClick={() => this.handlerQuantity(filho, 1, _option)} ></div>
											</div>
											<div className="col-sm-1 col-md-1 pull-rigth">
												<div className="custom-buttons-counter contador-personaliza">
													<span className="font-index font-contador-personaliza">{_.padStart(_option.currentQuantity == null ? _option.defaultQuantity : _option.currentQuantity, 2, '0')}</span>
												</div>
											</div>
										</div>
									</div>
								)
							})
						}
					</div>
				</div>
				<div className="max-width" id="sub-footer">
					<div style={{ height: "100px" }}>
						<div className="row text-center font-personaliza">
							<div className="btn-personaliza-cancela">
								<span className="text-btn-resumo font-btn-cancelar-personaliza" onClick={() => this.handlerCancel(filho)} >{this.props.strings.CANCEL}</span>
							</div>
							{this.hasChanges(filho) &&
								<div className="btn-personaliza-receita">
									<span className="text-btn-resumo " onClick={() => this.handlerOriginallyRecipe(filho)}  >{this.props.strings.RESTORE_ORIGINAL_RECIPE}</span>
								</div>
							}
							<div className="btn-personaliza-confirma" onClick={() => this.handlerConfirm(filho)}  >
								<span className="text-btn-resumo ">{this.props.strings.CONFIRM}</span>
							</div>
						</div>
					</div>
				</div>
			</div>
		)

		return this._renderHtmlAndLabel(html, { color: 'black', localizedLabel: 'PERSONALIZE DO SEU JEITO' }, type)
	}

	renderOption(option, label, type) {

		let html = _.map(option.sons.filter(opt=>!opt.included), (_option, index) => {
			return (
				<div key={`${Math.random()}`} className={`produto-combo text-center`} onClick={() => this.handleClickOption(option, _option)}>
					<div style={{ width: "120px", height: "120px", display: "block", margin: "auto", position: "relative" }}>
						<img src={BASE_URL + _option.imageUrl} alt="bg" className="width-produto" />
					</div>
					<div className="font-index" style={buttonStyle}>
						<p className="titulo-produto produtos-nome">{_option.localizedName}</p>
					</div>
				</div>
			)
		})

		if (option.minQuantity == 0) {
			html.push(
				<span key={`${Math.random()}`}><img src={require("../../images/not_cpf.png")} className="width-yes" alt="bg"
					onClick={() => this.handleClickOption(option, -1)} /></span>
			)
		}

		return this._renderHtmlAndLabel(html, label, type)
	}

	_renderHtmlAndLabel(html, label, type, button) {
		return <div key={`${Math.random()}`} className={`row`} >
			<span className="titulo-combo" style={{ color: label.color, paddingTop: "5px", paddingLeft: '4%' }}>{label.localizedLabel}</span>
			<div className="col-sm-12 col-md-12 produtos-combo" >
				{html}
			</div>
		</div>
	}


	customize(filho, custom) {
		filho.custom = custom
		this._save()
	}

	renderQuestion(filho, label, type) {
		let html = <div> <center key={`${Math.random()}`} className="form-group">
			<span><img style={{ height: '120px' }} src={require("../../images/yes_cpf.png")} className="width-yes" alt="bg"
				onClick={() => this.customize(filho, 'Y')} /></span>
			<span><img style={{ height: '120px' }} src={require("../../images/not_cpf.png")} className="width-yes" alt="bg"
				onClick={() => this.customize(filho, 'N')} /></span>
		</center><br /><br /></div>

		return this._renderHtmlAndLabel(html, label, type)
	}


	_renderSelected(selected, label, type) {
		let html = <div key={`${Math.random()}`} className={`row`}>
			<div className={`produto-combo-selecionado text-center`}>
				<div style={{ width: "120px", height: "120px", display: "block", margin: "auto", position: "relative" }}>
					<img src={BASE_URL + selected.imageUrl} alt="bg" className="width-produto" />
				</div>
				<div className="font-index" style={buttonStyle}>
					<p className="titulo-produto produtos-nome">{selected.localizedName}</p>
				</div>
			</div>
		</div>

		return this._renderHtmlAndLabel(html, label, type)
	}

	renderOptionSelected(option, label) {
		const hideOptions = (option.maxQuantity > 1)
		let selecteds = _.filter(option.sons, function (o) {
			return o.selected != undefined
		})
		_.each(selecteds, (selected, index) => {
			if (!hideOptions) {
				parts.push([this._renderSelected(selected, label), 1])
			}
			_.each(selected.sons, (neto, idx) => {
				if (!break_) {
					this.renderSon(neto, selected)
				}
			})
		})
	}

	renderSon(filho, parent) {
		if(filho.ignore) {
			return null
		}
		const partCodePai = parent.partCode
		const type = parent.partType
		if (filho.partType == 'Product' || filho.partType == 'Combo') {
			let options = _.orderBy(filho.sons, 'partType', 'asc')
			_.map(options, (op) => {
				if (!break_) {
					this.renderSon(op, filho)
				}
			})

		} else {

			var label = this.returnLabel(filho.partCode, partCodePai)
			if (filho.selected && filho.selected == 'Y') {
				this.renderOptionSelected(filho, label)
				return
			} else if ((filho.custom && filho.custom == 'N') || (filho.selected && filho.selected == 'N') || (type !== 'Product' && filho.minQuantity === 0)) {
				return null
			}
			else {
				break_ = true
			}

			if (filho.partType == 'Option' && filho.maxQuantity == 1) {
				parts.push([this.renderOption(filho, label, type), 1])
			} else {
				this.props.changeTextTop(parent.localizedName)
				parts.push([this.renderProduct(filho, label, "center"), 2])
			}

		}
	}

	_filterLayout2(layout) {
		var ret = []
		if (layout && layout[1] == 2) {
			ret.push(layout)
		}
		return ret
	}

	renderPartType(productOriginal) {
		const filteredSons = _.filter(productOriginal.sons, (son)=>!son.ignore || !(son.minQuantity === 0))
		if (filteredSons.length == 0) {
			this._save()
			return null
		}

		let options = _.orderBy(productOriginal.sons, ['partType', 'minQuantity'], ['asc', 'desc'])

		break_ = false
		parts = []
		_.map(options, (option) => {
			if (!break_) {
				return this.renderSon(option, productOriginal)
			}
			return null
		})

		let layout2 = parts.filter((f) => {
			return f[1] == 2
		})

		if (layout2.length == 0) {
			layout2 = parts
		}
		if (layout2.length == 0) {
			this._save()
			return null
		}
		return _.map(layout2, (option, index) => {
			if (option) {
				return <div className="options" key={index}>
					{option[0]}
				</div>
			}
			return null
		})

	}

	removeCustom(option) {
		delete option.custom
		option.sons = _.reduce(option.sons, (sons, op) => {
			if (!op.included){
				this.removeCustom(op)
				sons.push(op)
			}
			return sons
		}, [])
	}

	toBack(productOriginal) {
		let options = _.orderBy(productOriginal.sons, 'partType', 'asc').reverse()
		if (productOriginal.partType == 'Combo') {
			_.each(options, (option) => {
				if (option.partType == 'Product') {
					if (option.sons[0].custom) {
						delete option.sons[0].custom
						back = false
						this._save()
						return false
					}

				} else {
					if (option.selected) {
						_.remove(this.removeCustom(option), (p)=>!p.included)
						this.handlerOriginallyRecipe(option)
						back = false
						return false
					}
				}
			})
		} else if (productOriginal.partType == 'Product') {
			if (productOriginal.sons[0].custom) {
				delete productOriginal.sons[0].custom
				back = false
				this._save()
				return false
			}
		}
	}

	handlerGoBack() {

		let productOriginal = []

		_.each(this.props.productCurrent, (prod) => {
			if (prod.pendent != false) {
				productOriginal = prod
			}
		})

		back = true
		this.toBack(productOriginal)

		if (back) {

			if (this.props.oldSuggestion) {
				this.props.changeSubScreenAction(SUGGESTION_SCREEN)
			} else if ((this.props.couponData || []).length > 0) {
				this.props.changeSubScreenAction(COUPON_SCREEN)
			} else {
				this.props.changeTextTop(this.props.strings.CHOOSE_HERE)
				this.props.changeSubScreenAction(MAIN_SCREEN)
			}
		}
	}

	render() {

		if (this.state.loading || !this.props.productCurrent || this.props.productCurrent.length == 0) {
			return (
				<ReactLoading type="spin" color="#444" />
			)
		}

		let productCurrent = []

		_.each(this.props.productCurrent, (prod) => {
			if (prod.pendent != false) {
				productCurrent = prod
			}
		})

		if (productCurrent.length == 0) {
			return (
				<ReactLoading type="spin" color="#444" />
			)
		}

		if (productCurrent.response && productCurrent.response.status == 400) {
			return (
				<ReactLoading type="spin" color="#444" />
			)
		}

		if (productCurrent.localizedName) {
			this.props.changeTextTop(productCurrent.localizedName)
			this.props.alterUrlTopAction(productCurrent.imageUrl)
		}

		return (
			<div>
				<Top onGoBack={() => this.handlerGoBack()} />
				{/* <div className={`form-inline rolagem ${this.props.productCurrent[0].partType == "Product"? "div-personaliza-individual":""}  `} > */}
				<div className={`form-inline rolagem show-scroll`} ref={(el) => this.productRolagem = el}>
					{this.renderPartType(productCurrent)}
				</div>
				<SaleOptionsModal
					show={this.state.modalOption}
					options={this.state.productsToChoose}
					selected={this.state.modalOptionSelected}
					onOptionClick={(modalOptionSelected)=>this.setState({modalOptionSelected})}
					onClose={()=>this.setState({modalOption: false})}
					onConfirm={()=>this.handleConfirmOption(this.state.modalOptionSelected)}
				/>
			</div>

		)
	}
}

function mapStateToProps(state) {
	return {
		strings: state.strings,
		productCurrent: state.product.productCurrent,
		oldSuggestion: state.product.oldSuggestion,
		showSuggestion: state.product.showSuggestion,
		currentIndex: state.product.currentIndex,
		error: state.product.error,
		order: state.order,
		optionLabels: state.config.optionLabels,
		couponData: state.couponData,
		selectedSideMenu: state.selectedSideMenu,
	}
}

function mapDispatchToProps(dispatch) {
	return bindActionCreators({
		errorAction,
		changeSubScreenAction,
		alterProductAction,
		changeTextTop,
		saleSuggestedProductsAction,
		saleAddItemAction,
		alterUrlTopAction,
		expandedFooterAction,
		productSaleOptionsAction
	}, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(ProductScreen)