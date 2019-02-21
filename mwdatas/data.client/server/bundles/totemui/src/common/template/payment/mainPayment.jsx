import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import Top from '../ordered/top'
import { SALE_SCREEN } from '../../../common/constants'
import { changeScreenAction, changeTextTop, saleAddItemAction, saleRemoveItemAction, saleCancelAction } from './../../../actions'
import _ from 'lodash'
import { padZeros } from '../../common'
import BtnPlus from '../../images/PERSONALIZE-O-SEU-SANDUICHE/btn-mais.png'
import BtnMinus from '../../images/PERSONALIZE-O-SEU-SANDUICHE/btn-menos.png'
import BtnRemove from '../../images/PERSONALIZE-O-SEU-SANDUICHE/btn-excluir.png'
import Modal from '../../msg/modal'

// Retorna as classes da página de seleção de opçao de consumo
export class MainPayment extends Component {
    constructor(props){
        super(props)
        this.state = {
            showModal: false,
        }
    }
    getSize(size) {
        return {
            'S': '(PEQ)',
            'M': '(MED)',
            'L': '(GDE)'
        }[size] || ''
    }
    renderOrderItemsDetails = (rootItem, item = null, parent = null) => {
        if (!item) {
            item = rootItem
        }
        return _.map(item.sons, (details) => {
            if (details.ignore) {
                return false
            }
            if (details.partType == 'Product') {
                if (item.partType == 'Combo' && ((item.cfh && item.currentQuantity > 0) || ((details.currentQuantity || 0) !== details.defaultQuantity))) {
                    return (
                        <div className="details-text" key={`details_${item.partCode}_${details.partCode}`}>
                            {`${padZeros((details.currentQuantity || 1) * rootItem.currentQuantity, 2)} ${(details.localizedName || details.name)} ${this.getSize(details.size)}`}
                            <br />
                            {this.renderOrderItemsDetails(rootItem, details, item)}
                        </div>
                    )
                }
                else if (parent) {
                    if (parent.partType == 'Product' && (details.currentQuantity || 0) !== details.defaultQuantity) {
                        return (
                            <div className="indent-details-2x details-text" key={`details_${item.partCode}_${details.partCode}`}>
                                {`${details.currentQuantity > 0 ? "+" + padZeros((details.currentQuantity - details.defaultQuantity) * rootItem.currentQuantity, 2) : "SEM"} ${(details.localizedName || details.name)} ${this.getSize(details.size)}`}
                                <br />
                                {this.renderOrderItemsDetails(rootItem, details, item)}
                            </div>
                        )
                    }
                    else if (parent.partType == 'Combo' && details.currentQuantity > 0) {
                        return (
                            <div className="indent-details" key={`details_${item.partCode}_${details.partCode}`}>
                                {`${padZeros(details.currentQuantity * rootItem.currentQuantity, 2)} ${(details.localizedName || details.name)} ${this.getSize(details.size)}`}
                                <br />
                                {this.renderOrderItemsDetails(rootItem, details, item)}
                            </div>
                        )
                    }
                }
            }
            else if (details.partType == 'Combo' && !details.cfh) {
                return (
                    <div key={`details_${item.partCode}_${details.partCode}`}>
                        {`${padZeros((details.currentQuantity || 1) * rootItem.currentQuantity, 2)} ${(details.localizedName || details.name)} ${this.getSize(details.size)}`}
                        <br />
                        {this.renderOrderItemsDetails(rootItem, details, item)}
                    </div>

                )
            }
            if (details.partType === 'Combo' || details.partType === 'Option' || details.currentQuantity > 0) {
                return this.renderOrderItemsDetails(rootItem, details, item)
            }

        });
    }

    // renderOrderItemsDetailsCustom = (item) => {
    //     return _.map(item, (details) => {
    //         return (
    //             `${details.qty} ${details.text}`
    //         )
    //     }).join("\n");
    // }

    handlePlusItem(item) {
        item.currentQuantity++
        this.props.saleAddItemAction(this.props.order.sale_token, item).then((result) => {

        })
    }

    handleMinusItem(item) {
        if (_.reduce(this.props.order.items, (acc, item)=>acc+item.currentQuantity, 0) === 1) {
            this.setState({showModal: true})
        } else {
            item.currentQuantity--
            this.props.saleAddItemAction(this.props.order.sale_token, item).then((result) => {

            })
        }
    }

    handleRemoveItem(item) {
        if (this.props.order.items.length === 1 || (_.reduce(this.props.order.items, (acc, item)=>acc+item.currentQuantity, 0) - item.currentQuantity) === 0) {
            this.setState({showModal: true})
        } else {
            this.props.saleRemoveItemAction(this.props.order.sale_token, item.line).then((result) => {

            })
        }
    }

    renderOrderItems() {
        return _.map(this.props.order.items, (item) => {
            return (
                <div key={item.line} className="bg-itens-pedido-carrinho col-sm-12 col-md-12">
                    <div style={{position: 'absolute'}}>
                        <img className="btn-qty" src={BtnPlus} onClick={()=>this.handlePlusItem(item)} />
                        {item.currentQuantity > 0 && <img className="btn-qty" src={BtnMinus} onClick={()=>this.handleMinusItem(item)} />}
                        {item.currentQuantity > 0 && <img className="btn-qty" src={BtnRemove} onClick={()=>this.handleRemoveItem(item)} />}
                    </div>
                    <div className="pai-box-produto">
                        <div className="box-produto-rodape">
                            <div className="font-index descricao" style={{ color: "#3a1b0a" }}>
                                <p className="titulo-produto-pedido">{`${padZeros(item.currentQuantity, 2)} ${item.localizedName} ${this.getSize(item.size)}`}</p>
                                <div className="preco-porcao" style={{ whiteSpace: "pre-line", fontSize: "100%", lineHeight: "18px" }}>{this.renderOrderItemsDetails(item || [])}</div>
                                {/* <p className="preco-porcao" style={{ whiteSpace: "pre-line" }}>{this.renderOrderItemsDetailsCustom(item.customSnack || [])}</p> */}
                                <p className="valor-produto-rodape">{`R$ ${(parseFloat(item.totalPrice)*item.currentQuantity).toLocaleString(this.props.strings.LOCALE, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}</p>
                            </div>
                        </div>
                    </div>
                    <div className="bg-bottom-itens-pedido-carrinho"></div>
                </div>
            )
        })
    }

    // calcTotal() {
    //     var valorTotal = 0
    //     _.map(this.props.order.items, (item) => {
    //         valorTotal += item.totalPrice
    //     })
    //     return valorTotal.toLocaleString(this.props.strings.LOCALE, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    //     // return _.reduce(this.props.order.items, (total, item) => total + parseFloat(item.price) + _.reduce(item.customSnack, (totalCustom, itemCustom) => totalCustom + (itemCustom.priceUnity * itemCustom.qty), 0), 0).toLocaleString(this.props.strings.LOCALE, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    // }

    handlerGoBack() {
        this.props.changeTextTop(this.props.strings.CHOOSE_HERE)
        this.props.changeScreenAction(SALE_SCREEN)
    }

    handleCloseModal = () => {
        this.setState({showModal: false})
    }
    render() {
        return (
            <div>
                <Top onGoBack={() => this.handlerGoBack()} />
                <div className="max-width row">
                    <div className="form-inline rolagem show-scroll" style={{ paddingLeft: "16px" }}>
                        <div className="col-sm-12 col-md-12">
                            <p className="font-index titulo text-line-height" style={{ color: "black" }}>{this.props.strings.ORDER_CORRECT}</p>
                        </div>
                        {this.renderOrderItems()}
                    </div>
                </div>
                <Modal
                    showModal={this.state.showModal}
                    divCenter={this.props.strings.CANCEL_ORDER_CONFIRM}
                    onConfirm={()=>this.props.saleCancelAction(this.props.order.sale_token)}
                    onCancel={this.handleCloseModal}
                    onClose={this.handleCloseModal}
                    okButtonText={this.props.strings.YES}
                    cancelButtonText={this.props.strings.NO}
                    showCancel
                />
            </div>

        )
    }
}

function mapStateToProps(state) {
    return {
        order: state.order,
        strings: state.strings
    }
}

function mapDispatchToProps(dispatch) {
    return bindActionCreators({
        changeScreenAction,
        changeTextTop,
        saleAddItemAction,
        saleRemoveItemAction,
        saleCancelAction
    }, dispatch)
}


export default connect(mapStateToProps, mapDispatchToProps)(MainPayment)