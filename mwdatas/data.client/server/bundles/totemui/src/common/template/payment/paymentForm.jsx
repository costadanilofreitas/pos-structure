import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { changeScreenAction, modalAction, saleAddPaymentAction, saleCheckPaymentAction, saleApagarChangedAction, saleCancelAction, cleanUpAction, errorAction, alterTimeCounterAction } from '../../../actions'
import Grid from '../../layout/grid'
import Top from '../ordered/top'
import Modal from '../../msg/modal'
// import ModalPaymentFlux from '../../msg/modalPaymentFlux'
import ModalMoneyPartial from '../../msg/modalMoneyPartial'
import { NAME_SCREEN, START_SCREEN } from '../../constants'

const FULL_PAYMENT = 'FULL_PAYMENT'
const SPLIT_PAYMENT = 'SPLIT_PAYMENT'

export class PaymentForm extends Component {

    constructor(props) {
        super(props);

        this.state = {
            cancel: true,
            modalFlux: false,
            modalPartial: false,
            modalCancel: false,
            modalPIN: false,
            PIN: '',
            paymentMode: null,
            partialAmount: null
        }
    }

    _aPagar() {
        if (this.props.order.aPagar) {
            return Number(this.props.order.aPagar)
        }

        return this._calcTotalPrice()
    }

    _calcTotalPrice() {
        let valorTotal = 0
        _.map(this.props.order.items, (item) => {
            valorTotal += Number(item.totalPrice) * Number(item.currentQuantity)
        })

        return valorTotal
    }

    handleAlterMoney() {
        this.setState({ modalPartial: true })
        this.props.modalAction("show")
    }

    handlerModalPaymentForm = (type) => {
        const value = (this.state.paymentMode === SPLIT_PAYMENT ? this.state.partialAmount : this._aPagar()).toFixed(2)
        let typePayment = { type, value }
        this.props.saleAddPaymentAction(this.props.order.sale_token, typePayment).then((data) => {
            this.setState({
                titleHeader: this.props.strings.ORDER_PAYMENT,
                titleBody: <span style={{ whiteSpace: "pre-line" }}>AGUARDE</span>,
                divCenter: <img src={require('../../../common/images/TELA-DE-PAGAMENTO/img_pegar_pedido.png')} className='bg-pagamento-modal-recido' alt='Recibo' />,
                additional: null

            })
            this.checkPayment()
        })
    }

    closeModalOnPartial = () => {
        this.setState({ modalFlux: false, modalPartial: false })
    }

    handleModal = () => {

    }

    // FLUX INICIO

    hideFlux() {
        this.setState({
            modalFlux: false,
        })
    }

    checkPayment = () => {
        if (this.props.order.sale_token) {
            this.props.alterTimeCounterAction(0)

            this.setState({
                modalFlux: true,
            })

            this.props.saleCheckPaymentAction(this.props.order.sale_token).then((data) => {
                if (data.payload.message) {
                    this.props.errorAction(data)
                } else if (data.error) {
                    if (data.payload.response && data.payload.response.data)
                        var msg = data.payload.response.data

                    this.setState({
                        titleHeader: this.props.strings.DONE,
                        titleBody: msg,
                        divCenter: '',
                    })
                    this.showMessage(msg)

                } else {
                    switch (data.payload.data[0]) {
                        case 200: // order paid
                            {
                                this._finishPayment()
                                break
                            }
                        case 201: // payment done, order pending
                            {
                                this.props.saleApagarChangedAction(data.payload.data[1])
                                this._finishPartial()
                                break
                            }
                        case 202: // message confirmation
                            {
                                let msg = data.payload.data[1]
                                this.setState({
                                    titleBody: <span style={{ whiteSpace: "pre-line" }}>{data.payload.data[1]}</span>,
                                    modalPIN: true,
                                    modalFlux: false
                                })
                                break
                            }
                        case 400: // invalid data
                            {
                                let msg = data.payload.data[1]
                                this.setState({
                                    titleBody: <span style={{ whiteSpace: "pre-line" }}>{data.payload.data[1]}</span>,
                                })
                                this.showMessage(msg)
                                this.setState({cancel: false})
                                break
                            }
                        case 300: // fiscal data processing, can't cancel anymore
                            {
                                let msg = data.payload.data[1]
                                this.setState({
                                    titleBody: <span style={{ whiteSpace: "pre-line" }}>{data.payload.data[1]}</span>,
                                    cancel: false
                                })
                                this.checkPayment()
                                break
                            }
                        case 102: // pending information
                            {
                                let msg = data.payload.data[1]
                                this.setState({
                                    titleBody: <span style={{ whiteSpace: "pre-line" }}>{data.payload.data[1]}</span>,
                                    cancel: true
                                })
                                this.checkPayment()
                                break
                            }
                        case 500:
                            {
                                let msg = data.payload.data[1]
                                this.setState({
                                    cancel: false,
                                    titleBody: <span style={{ whiteSpace: "pre-line" }}>{data.payload.data[1]}</span>,
                                })
                                setTimeout(()=>{
                                    this.hideFlux()
                                    this.props.changeScreenAction(START_SCREEN)
                                    this.props.saleCancelAction(this.props.order.sale_token)
                                }, 5000)
                            }
                    }
                }
            })
        }
    }

    showMessage(message) {
        this.setState({
            modalFlux: true,
            titleHeader: this.props.strings.ORDER_PAYMENT,
            titleBody: <span style={{ whiteSpace: "pre-line" }}>{message}</span>,
            divCenter: <img src={require('../../../common/images/TELA-DE-PAGAMENTO/img_pagamento_pedido.png')} className='bg-pagamento-modal-hamburger' alt='Hamburger' />,
        })

        setTimeout(() => this.hideFlux(), 3000)
    }

    _finishPartial() {
        this.setState({
            cancel: false,
            modalFlux: true,
            titleHeader: this.props.strings.DONE,
            titleBody: <span style={{ whiteSpace: "pre-line" }}>PAGAMENTO PARCIAL CONCLUÍDO</span>,
            divCenter: <img src={require('../../../common/images/TELA-DE-PAGAMENTO/img_pagamento_pedido.png')} className='bg-pagamento-modal-hamburger' alt='Hamburger' />,
        })

        setTimeout(() => {
            this.setState({partialAmount: null})
            this.hideFlux()
        }, 5000)
    }

    _finishPayment() {
        this.setState({
            cancel: false,
            modalFlux: true,
            titleHeader: this.props.strings.DONE,
            titleBody: <span style={{ whiteSpace: "pre-line" }}>POR FAVOR RETIRE SUA NOTA</span>,
            divCenter: <img src={require('../../../common/images/TELA-DE-PAGAMENTO/img_pagamento_pedido.png')} className='bg-pagamento-modal-hamburger' alt='Hamburger' />,
        })

        setTimeout(() => this._finishPayment2(), 5000)
    }

    _finishPayment2 = () => {
        this.setState({
            modalFlux: true,
            titleHeader: this.props.strings.DONE,
            titleBody: <span style={{ whiteSpace: "pre-line" }}>{this.props.strings.ORDER_COMPLETE_ADDITIONAL}</span>,
            divCenter: <img src={require('../../../common/images/TELA-DE-PAGAMENTO/img_pedido_realizado.png')} className='bg-pagamento-modal-finalizar' alt='Finalizado' />,
            additional: <span style={{ whiteSpace: "pre-line" }}>{this.props.strings.ORDER_COMPLETE}</span>
        })

        setTimeout(() => this._finishPayment3(), 8000)
    }

    _finishPayment3 = () => {
        // this.props.modalAction("fade")
        this.hideFlux()
        this.props.changeScreenAction(START_SCREEN)
        this.props.cleanUpAction()
    }

    handleValue(value) {
        this.setState({ PIN: this.state.PIN + value })
    }

    handleBack() {
        const value = this.state.PIN
        this.setState({ PIN: value.substr(0, value.length - 1) })
    }

    isValidNull() {
        if (this.state.PIN && this.state.PIN.length > 0) {
            return true
        }
        return false
    }

    handleCancelPin() {
        this.props.saleCheckPaymentAction(this.props.order.sale_token, 'cancel').then(data => {
            this.setState({
                modalPIN: false,
                PIN: ''
            })
            this.checkPayment()
        })
    }

    handleConfirmPin() {
        this.props.saleCheckPaymentAction(this.props.order.sale_token, this.state.PIN).then(data => {
            this.setState({
                modalPIN: false,
                PIN: ''
            })
            this.checkPayment()
        })
    }

    handlerCancel() {
        this.props.saleCheckPaymentAction(this.props.order.sale_token, 'cancel')
    }

    renderModalPIN() {
        return <div className={'modal show'} id="modalCPF" tabIndex="-1" role="dialog" data-backdrop="static" data-keyboard="false" aria-labelledby="myModalLabel" style={{ backgroundColor: "rgba(100,100,100,0.6)" }}>
            <div className="vertical-alignment-helper">
                <div className="modal-dialog vertical-align-center">
                    <div id="bodyModal" className="modal-selecao modal-content">
                        <div className="bg-modal">
                            <div className="bg-modal-int-cpf">
                                <div className="modal-header">
                                    <div className="max-width row">
                                        <div className="form-inline">

                                            <div className="col-sm-10 col-md-8 text-left">
                                                <h4 className="modal-title-cpf"></h4>
                                            </div>

                                        </div>
                                    </div>
                                </div>

                                <div className="modal-body">
                                    <div className="max-width row" style={{ marginTop: "35px" }}>
                                        {/* <p className="titulo-produto titulo-body-modal" style={{ marginTop: '20px', height: '50px' }}>{this.state.titleBody}</p> */}
                                        <div className="col-sm-12 col-md-12 ">
                                            <p className="titulo-produto" style={{ paddingTop: "36px", textAlign: "center" }}>{this.state.titleBody}</p>
                                        </div>

                                        <div className="col-sm-12 col-md-12 ">
                                            <div className="bg-input-cpf">
                                                <span className="text-btn-resumo titulo-produto text-line-height">{this.state.PIN}</span>
                                            </div>

                                        </div>

                                        <div className="col-sm-12 col-md-12 ">
                                            <div className="text-center bnt-cpf" onClick={() => this.handleValue(1)}>
                                                <span>1</span>
                                            </div>
                                            <div className="text-center bnt-cpf" onClick={() => this.handleValue(2)}>
                                                <span>2</span>
                                            </div>
                                            <div className="text-center bnt-cpf bnt-cpf-last" onClick={() => this.handleValue(3)}>
                                                <span>3</span>
                                            </div>
                                            <div className="text-center bnt-cpf" onClick={() => this.handleValue(4)} >
                                                <span>4</span>
                                            </div>
                                            <div className="text-center bnt-cpf" onClick={() => this.handleValue(5)}>
                                                <span>5</span>
                                            </div>
                                            <div className="text-center bnt-cpf bnt-cpf-last" onClick={() => this.handleValue(6)}>
                                                <span>6</span>
                                            </div>
                                            <div className="text-center bnt-cpf" onClick={() => this.handleValue(7)}>
                                                <span>7</span>
                                            </div>
                                            <div className="text-center bnt-cpf" onClick={() => this.handleValue(8)}>
                                                <span>8</span>
                                            </div>
                                            <div className="text-center bnt-cpf  bnt-cpf-last" onClick={() => this.handleValue(9)}>
                                                <span>9</span>
                                            </div>
                                            <div className="text-center bnt-cpf">

                                            </div>
                                            <div className="text-center bnt-cpf" onClick={() => this.handleValue(0)}>
                                                <span>0</span>
                                            </div>
                                            <div className="text-center bnt-cpf  bnt-cpf-last">
                                                <img src={require('../../../common/images/NOTA-FISCAL-CPF/seta_CPF.png')} className="btn-arrow-back" alt="Shift" onClick={() => this.handleBack()} />
                                            </div>
                                        </div>

                                    </div>

                                    <div className="col-sm-12 col-md-12" style={{ paddingTop: "49px" }}>
                                        <div className="row">
                                            <div className="col-sm-6 col-md-6 text-left no-padding">


                                                <div className="btn-nao-modal text-center">
                                                    <span className="text-btn-cpf" onClick={() => this.handleCancelPin()}>{this.props.strings.CANCEL}</span>
                                                </div>

                                            </div>
                                            {this.isValidNull() &&
                                                <div className="col-sm-6 col-md-6 text-left no-padding">
                                                    <div className="btn-confirmar-modal text-center">
                                                        <span className="text-btn-cpf" onClick={() => this.handleConfirmPin()} >{this.props.strings.CONFIRM}</span>
                                                    </div>
                                                </div>
                                            }

                                        </div>
                                    </div>

                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

    }

    renderModalFlux = () => {
        return (
            <div className={`modal show`} id="modalFluxoPagamento" tabIndex="-1" role="dialog" data-backdrop="static" data-keyboard="false" aria-labelledby="myModalLabel" style={{ backgroundColor: "rgba(100,100,100,0.6)" }}>
                <div className="vertical-alignment-helper">
                    <div className="modal-dialog vertical-align-center">
                        <div id="bodyModal" className="modal-selecao modal-content">
                            <div className="bg-modal">
                                <div className="bg-modal-int" style={{ backgroundSize: '551px 450px', height: '450px' }}>
                                    <div className="modal-header">
                                        <div className="max-width row">
                                            <div className="form-inline">
                                                <div className="col-sm-10 col-md-8 text-left">
                                                    <h4 className="modal-title titulo-produto">{this.state.titleHeader}</h4>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="modal-body">
                                        <div className="max-width row">
                                            <div className="col-sm-12 col-md-12">
                                                <div className="font-index text-center" style={{ color: '#3a1b0a' }}>
                                                    <p className="titulo-produto titulo-body-modal" style={{ marginTop: '50px', height: '50px' }}>{this.state.titleBody}</p>
                                                </div>
                                            </div>
                                            <div id="divcentro" className="col-sm-12 col-md-12 ">
                                                {this.state.divCenter}
                                            </div>
                                            { this.state.additional ?
                                                <div className="col-sm-12 col-md-12">
                                                    <div className="font-index text-center" style={{ color: '#3a1b0a' }}>
                                                        <p className="titulo-produto titulo-body-modal" style={{height: '50px' }}>{this.state.additional}</p>
                                                    </div>
                                                </div>
                                                : null
                                            }
                                        </div>
                                        <div className="max-width row">
                                            <div className="col-sm-12 col-md-12">
                                                {this.state.cancel &&
                                                    <center style={{ marginTop: '30px' }}>
                                                        <div className="btn-nao-modal text-center">
                                                            <span className="text-btn-cpf" onClick={() => this.handlerCancel()}>{this.props.strings.CANCEL}</span>
                                                        </div>
                                                    </center>
                                                }
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

    handlePartialConfirm = (value) => {
        this.setState({partialAmount: value})
    }
    handlePartialCancel = () => {
        if (this.props.order.aPagar && this.props.order.aPagar != this._calcTotalPrice()) {
            this.setState({modalCancel: true})
        } else {
            this.setState({paymentMode: null, partialAmount: null})
        }
    }
    renderModal() {
        if (this.state.modalFlux) {
            return this.renderModalFlux()
        } else if (this.state.modalPIN) {
            return this.renderModalPIN()
        } else {
            return <ModalMoneyPartial
                key={`${Math.random()}`}
                showModal={this.state.paymentMode === SPLIT_PAYMENT && !this.state.partialAmount}
                aPagar={this._aPagar()}
                total={this._calcTotalPrice()}
                onConfirm={this.handlePartialConfirm}
                onCancel={this.handlePartialCancel}
            />
        }
    }

    // FLUX FIM

    handlerGoBack() {
        switch(this.state.paymentMode) {
        case FULL_PAYMENT:
            this.setState({paymentMode: null})
            break
        case SPLIT_PAYMENT:
            this.setState({partialAmount: null})
            break
        default:
            this.props.changeScreenAction(NAME_SCREEN)
        }
    }

    handleSetPaymentMode(paymentMode) {
        this.setState({paymentMode})
    }

    handleClearPaymentMode = () => {
        this.setState({paymentMode: null})
    }

    handleCloseCancelModal = () => {
        this.setState({modalCancel: false})
    }

    handleConfirmCancelModal = () => {
        this.props.saleCancelAction(this.props.order.sale_token)
    }

    render() {
        const mode = this.state.paymentMode
        return (
            <div>
                <Top onGoBack={() => this.handlerGoBack()} />
                <div className="max-width row">
                    {mode === FULL_PAYMENT || Number(this.state.partialAmount) ?
                        <div className="form-inline" style={{ paddingLeft: '16px', paddingRight: '11px' }}>
                            <Grid cols="0 12 12">
                                <p className="font-index titulo text-line-height" style={{ color: 'black' }}>{this.props.strings.CHOOSE_PAYMENT_TYPE}</p>
                            </Grid>
                            <Grid cols="0 12 12" className="bg-itens-pedido-carrinho" onClick={() => this.handlerModalPaymentForm('2')} >
                                <div className="bg-forma-pagamento">
                                    <div className="divs-bg-pagamento">
                                        <p className="font-index titulo text-line-height" style={{ color: 'black', float: 'left' }}>DÉBITO</p>
                                        <img src={require('../../../common/images/TELA-DE-PAGAMENTO/cartao_visa.png')} className="bandeiras-cartao-visa" alt="Visa" />
                                        <img src={require('../../../common/images/TELA-DE-PAGAMENTO/cartao_mastercard.png')} className="bandeiras-cartao-master" alt="mastercard" />
                                        <img src={require('../../../common/images/TELA-DE-PAGAMENTO/cartao_americaexpress.png')} className="bandeiras-cartao-america" alt="mastercard" />
                                    </div>
                                </div>
                            </Grid>
                            <Grid cols="0 12 12" className="bg-itens-pedido-carrinho" onClick={() => this.handlerModalPaymentForm('1')} >
                                <div className="bg-forma-pagamento">
                                    <div className="divs-bg-pagamento">
                                        <p className="font-index titulo text-line-height" style={{ color: 'black', float: 'left' }}>CRÉDITO</p>
                                        <img src={require('../../../common/images/TELA-DE-PAGAMENTO/cartao_visa.png')} className="bandeiras-cartao-visa cartao-visa-credito" alt="Visa" />
                                        <img src={require('../../../common/images/TELA-DE-PAGAMENTO/cartao_mastercard.png')} className="bandeiras-cartao-master" alt="mastercard" />
                                        <img src={require('../../../common/images/TELA-DE-PAGAMENTO/cartao_americaexpress.png')} className="bandeiras-cartao-america" alt="mastercard" />
                                    </div>
                                </div>
                            </Grid>
                            <Grid cols="0 12 12" className="bg-itens-pedido-carrinho" onClick={() => this.handlerModalPaymentForm('2')} >
                                <div className="bg-forma-pagamento">
                                    <div className="divs-bg-pagamento">
                                        <p className="font-index titulo text-line-height" style={{ color: 'black', float: 'left' }}>REFEIÇÃO</p>
                                        <div className="divs-pagamento-alimentacao">
                                            <img src={require('../../../common/images/TELA-DE-PAGAMENTO/cartao_diners.png')} className="bandeiras-cartao-diners cartao-visa-credito" alt="Visa" />
                                            <img src={require('../../../common/images/TELA-DE-PAGAMENTO/cartao_elo.png')} className="bandeiras-cartao-elo" alt="mastercard" />
                                            <img src={require('../../../common/images/TELA-DE-PAGAMENTO/cartao_alelo.png')} className="bandeiras-cartao-aelo" alt="mastercard" />
                                        </div>
                                        <p className="segunda-linha-restaurante">
                                            <img src={require('../../../common/images/TELA-DE-PAGAMENTO/cartao_ticket.png')} className="bandeiras-cartao-ticket" alt="mastercard" />
                                            <img src={require('../../../common/images/TELA-DE-PAGAMENTO/cartao_sodexo.png')} className="bandeiras-cartao-sodexo" alt="mastercard" />
                                        </p>
                                    </div>
                                </div>
                            </Grid>
                            <center className="sale-total">
                                <div className="font-index text-center" style={{ color: "black" }}>
                                    <p className="font-index titulo text-line-height">{`${this.props.strings.ORDER_TOTAL}${this.state.partialAmount ? ' (PARCIAL)' : ''}`}:
                                    <span style={{ color: "black" }}> R$ {(this.state.partialAmount || this._aPagar()).toLocaleString(this.props.strings.LOCALE, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                                    </p>
                                </div>
                            </center>
                            {/* DIVISÃO DE PAGAMENTO */}

                            {/* <center>
                                <div className="font-index text-center" style={{ color: "#255576" }}>
                                    <p className="font-index titulo text-line-height">{this.props.strings.ORDER_TOTAL}:
                                    <span style={{ color: "black" }}> R$ {this._aPagar().toLocaleString(this.props.strings.LOCALE, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                                    </p>
                                </div>
                                <div className="btn-green text-center" style={{ width: '400px' }} onClick={() => this.handleAlterMoney()}>
                                    <span className="text-btn-cpf">PAGAR OUTRO VALOR</span>
                                </div>
                            </center> */}
                        </div>
                        :
                        <div className="form-inline" style={{ paddingLeft: '16px', paddingRight: '11px' }}>
                            <Grid cols="0 12 12">
                                <p className="font-index titulo text-line-height" style={{ color: 'black' }}>COMO DESEJA PAGAR A CONTA?</p>
                            </Grid>
                            <Grid cols="0 12 12" onClick={() => this.handleSetPaymentMode(SPLIT_PAYMENT)} >
                                <div className="bg-forma-pagamento bg-pagto-dividido">
                                    <div className="divs-bg-pagamento" style={{width: '90%'}}>
                                        <div className="font-index titulo text-line-height">QUERO RACHAR A CONTA</div>
                                    </div>
                                </div>
                            </Grid>
                            <Grid cols="0 12 12" className="bg-itens-pedido-carrinho" onClick={() => this.handleSetPaymentMode(FULL_PAYMENT)} >
                                <div className="bg-forma-pagamento bg-pagto-inteiro">
                                    <div className="divs-bg-pagamento" style={{width: '90%'}}>
                                        <p className="font-index titulo text-line-height">PAGAR O VALOR TOTAL</p>
                                    </div>
                                </div>
                            </Grid>
                            <center className="sale-total">
                                <div className="font-index text-center" style={{ color: "black" }}>
                                    <p className="font-index titulo text-line-height">{this.props.strings.ORDER_TOTAL}:
                                    <span style={{ color: "black" }}> R$ {this._aPagar().toLocaleString(this.props.strings.LOCALE, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                                    </p>
                                </div>
                            </center>
                            {/* DIVISÃO DE PAGAMENTO */}

                            {/* <center>
                                <div className="font-index text-center" style={{ color: "#255576" }}>
                                    <p className="font-index titulo text-line-height">{this.props.strings.ORDER_TOTAL}:
                                    <span style={{ color: "black" }}> R$ {this._aPagar().toLocaleString(this.props.strings.LOCALE, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                                    </p>
                                </div>
                                <div className="btn-green text-center" style={{ width: '400px' }} onClick={() => this.handleAlterMoney()}>
                                    <span className="text-btn-cpf">PAGAR OUTRO VALOR</span>
                                </div>
                            </center> */}
                        </div>
                    }
                    {this.renderModal()}
                    <Modal
                        showModal={this.state.modalCancel}
                        divCenter={this.props.strings.CANCEL_ORDER_CONFIRM}
                        onConfirm={this.handleConfirmCancelModal}
                        onCancel={this.handleCloseCancelModal}
                        onClose={this.handleCloseCancelModal}
                        okButtonText={this.props.strings.YES}
                        cancelButtonText={this.props.strings.NO}
                        showCancel
                    />
                </div>
            </div>
        )
    }
}


function mapStateToProps(state) {
    return {
        selectedScreen: state.selectedScreen,
        strings: state.strings,
        order: state.order,
    }
}

function mapDispatchToProps(dispatch) {
    return bindActionCreators({
        saleCheckPaymentAction,
        changeScreenAction,
        modalAction,
        saleAddPaymentAction,
        saleApagarChangedAction,
        errorAction,
        alterTimeCounterAction,
        saleCancelAction,
        cleanUpAction
    }, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(PaymentForm)