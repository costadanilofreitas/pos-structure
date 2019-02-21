import React, { Component } from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { NAME_SCREEN, PAYMENT_SCREEN, PAYMENT_FORM_SCREEN, COUPON_KEYBOARD, MAIN_SCREEN, SALE_SCREEN } from '../../constants'
import { changeSubScreenAction, changeScreenAction, changeTextTop, saleAddCustomerInfoAction, cupomAction } from '../../../actions'
import Modal from '../../msg/modal'
import ModalCoupon from '../../msg/modalCoupon'


const textStyle = {
    color: "#3a1b0a"
}

export class FooterKeyBoard extends Component {
    constructor(props) {
        super(props);
        this.state = {
            titleHeader: "ATENÇÃO!",
            titleBody: "",
            divCenter: "",
            type: "nome",
            lowerButton: false
        };
    }

    handlerCancel = () => {
        switch (this.props.selectedScreen) {
            case NAME_SCREEN:
                this.props.changeScreenAction(PAYMENT_SCREEN)
                break;
            case COUPON_KEYBOARD:
                this.props.changeTextTop(this.props.strings.CHOOSE_HERE)
                this.props.changeScreenAction(SALE_SCREEN)
                break;
        }
        this.props.changeSubScreenAction(MAIN_SCREEN)
    }

    handlerConfirm = () => {
        if (this.props.selectedScreen == NAME_SCREEN) {
            if (this.props.order.clientName.length == 0) {
                this.setState({
                    titleHeader: this.props.strings.WARNING,
                    titleBody: "",
                    divCenter: this.props.strings.TYPE_YOUR_NAME,
                    type: "alert",
                    lowerButton: false
                });
            }
            else {
                let data = { "name": this.props.order.clientName, "document": this.props.order.cpf }
                this.props.saleAddCustomerInfoAction(this.props.order.sale_token, data).then((data) => {
                    if (data && data.payload && data.payload.data.length > 0) {
                        this.setState({type: "alert", lowerButton: true, titleBody: <span style={{fontSize: '20pt', lineHeight: '1.2', whiteSpace: 'pre-wrap'}}>{data.payload.data.replace(/\\/g, '\n')}</span>})
                    } else {
                        this.props.changeScreenAction(PAYMENT_FORM_SCREEN);
                    }
                })
            }
        } else {
            this.props.cupomAction(this.props.order.couponCode).then((data) => {
                if (data.error) {
                    this.setState({ type: "alert", titleBody: "", divCenter: this.props.strings.INVALID_COUPON, lowerButton: false })
                } else {
                    this.setState({ type: "coupon", lowerButton: false })
                }
            })


            // if (!this.couponIsValid())
            //     this.setState({ type: "alert", titleBody: "", divCenter: this.props.strings.INVALID_COUPON })
            // else
            //     this.setState({ type: "coupon" })

        }
    }

    handleCloseAlert = () => {
        this.setState({type: "nome"})
    }

    renderFooter = () => {
        switch (this.props.selectedScreen) {
            case NAME_SCREEN:
                return <Modal
                    showModal={this.state.type === 'alert'}
                    titleHeader={this.state.titleHeader}
                    titleBody={this.state.titleBody}
                    divCenter={this.state.divCenter}
                    onConfirm={this.handleCloseAlert}
                    onCancel={this.handleCloseAlert}
                    onClose={this.handleCloseAlert}
                    lowerButton={this.state.lowerButton}
                />
            case COUPON_KEYBOARD:
                return (
                    <div>
                        <ModalCoupon
                            showModal={this.state.type === 'coupon'}
                            onClose={this.handleCloseAlert}
                        />
                        <Modal
                            showModal={this.state.type === 'alert'}
                            titleHeader={this.state.titleHeader}
                            titleBody={this.state.titleBody}
                            divCenter={this.state.divCenter}
                            onConfirm={this.handleCloseAlert}
                            onCancel={this.handleCloseAlert}
                            onClose={this.handleCloseAlert}
                            lowerButton={this.state.lowerButton}
                        />
                    </div>
                )
        }
    }

    // couponIsValid = () => {

    //     if (this.props.order.couponCode == "123456")
    //         return true
    //     else
    //         return false;
    // }

    render() {
        return (
            <footer>
                <div className="max-width">
                    <div id="detalhePedido" className="row resumo-pedido-open-fluxo">
                        <div className={`col-sm-12 col-md-12  div-btns-resumo  ${this.props.selectedScreen == COUPON_KEYBOARD ? "div-btns-resumo-coupon" : ""} `}>
                            <div className="row">
                                <div className="col-sm-6 col-md-6 text-left">
                                    <div className="btn-cancelar-pedido text-center">
                                        <span className="text-btn-resumo" onClick={this.handlerCancel} > {this.props.strings.CANCEL}</span>
                                    </div>

                                </div>
                                <div className="col-sm-6 col-md-6 text-left">
                                    <div className="btn-finalizar-pedido text-center">
                                        <span className="text-btn-resumo" onClick={this.handlerConfirm} >{this.props.strings.CONFIRM}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                {this.renderFooter()}
            </footer>
        )
    }
}

function mapStateToProps(state) {
    return {
        selectedScreen: state.selectedScreen,
        order: state.order,
        strings: state.strings
    }
}

function mapDispatchToProps(dispatch) {
    return bindActionCreators({
        changeScreenAction,
        changeSubScreenAction,
        cupomAction,
        saleAddCustomerInfoAction,
        changeTextTop
    }, dispatch)
}


export default connect(mapStateToProps, mapDispatchToProps)(FooterKeyBoard)