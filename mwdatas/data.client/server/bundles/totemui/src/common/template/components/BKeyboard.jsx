
import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import Top from '../ordered/top'
import { changeClientNameAction, changeCouponAction, changeScreenAction, changeTextTop } from '../../../actions'
import Keyboard from '../../layout/keyboard'
import Grid from '../../layout/grid'
import { NAME_CLIENT, COUPON, COUPON_KEYBOARD, NAME_SCREEN, PAYMENT_SCREEN, SALE_SCREEN } from '../../constants'


// Retorna as classes da página de seleção de opçao de consumo
export class BKeyboard extends Component {
    constructor(props) {
        super(props)
    }

    handleValue(value) {
        const clientName = this.props.order.clientName || ""
        const couponCode = this.props.order.couponCode || ""
        if (this.props.screen == NAME_SCREEN && clientName.length < 18) {
            this.props.changeClientNameAction(clientName + value)
        }
        else if (this.props.screen == COUPON_KEYBOARD && couponCode.length < 18)
            this.props.changeCouponAction(couponCode + value)
    }

    handleBack() {

        if (this.props.screen == NAME_SCREEN) {
            const value = this.props.order.clientName
            this.props.changeClientNameAction(value.substr(0, value.length - 1))
        }

        else if (this.props.screen == COUPON_KEYBOARD) {
            const value = this.props.order.couponCode
            this.props.changeCouponAction(value.substr(0, value.length - 1))
        }
    }



    renderNumeric = show => {
        if (show == "true") {
            return (
                <Grid className="bg-itens-pedido-carrinho" >
                    <Keyboard value='1' className='btn-cliente' onClick={() => this.handleValue(1)} />
                    <Keyboard value='2' onClick={() => this.handleValue(2)} />
                    <Keyboard value='3' onClick={() => this.handleValue(3)} />
                    <Keyboard value='4' onClick={() => this.handleValue(4)} />
                    <Keyboard value='5' onClick={() => this.handleValue(5)} />
                    <Keyboard value='6' onClick={() => this.handleValue(6)} />
                    <Keyboard value='7' onClick={() => this.handleValue(7)} />
                    <Keyboard value='8' onClick={() => this.handleValue(8)} />
                    <Keyboard value='9' onClick={() => this.handleValue(9)} />
                    <Keyboard value='0' onClick={() => this.handleValue(0)} className='bnt-cpf-last' />
                </Grid >
            )
        }
    }

    handleSubtitle = () => {
        switch (this.props.subtitle) {
            case "1":
                return this.props.strings.NAME_PROMPT
            case "2":
                return this.props.strings.COUPON_PROMPT
        }
    }

    handleFontSubtitle = () => {
        switch (this.props.subtitle) {
            case "1":
                return "font-index titulo text-line-height"
            case "2":
                return "font-index subtitulo-cupom text-line-height"
        }
    }

    handlerGoBack() {
        if (this.props.screen == COUPON_KEYBOARD) {
            this.props.changeTextTop(this.props.strings.CHOOSE_HERE)
            this.props.changeScreenAction(SALE_SCREEN)
        } else {
            this.props.changeScreenAction(PAYMENT_SCREEN)
        }
    }

    render() {
        return (
            <div>

                <Top onGoBack={() => this.handlerGoBack()} />
                <div className="max-width row">
                    <div className="form-inline">
                        <Grid >
                            <p className={this.handleFontSubtitle()} style={{ color: "black" }}> {this.handleSubtitle()} </p>
                        </Grid >
                        <Grid >
                            <div className="bg-input-name">
                                <span className="text-btn-resumo">{this.props.screen == NAME_SCREEN ? this.props.order.clientName : this.props.order.couponCode}</span>
                            </div>
                        </Grid >
                        {this.renderNumeric(this.props.numericKeyboard)}
                        <Grid className="bg-itens-pedido-carrinho" >
                            <Keyboard value='Q' className='btn-cliente' onClick={() => this.handleValue("Q")} />
                            <Keyboard value='W' onClick={() => this.handleValue("W")} />
                            <Keyboard value='E' onClick={() => this.handleValue("E")} />
                            <Keyboard value='R' onClick={() => this.handleValue("R")} />
                            <Keyboard value='T' onClick={() => this.handleValue("T")} />
                            <Keyboard value='Y' onClick={() => this.handleValue("Y")} />
                            <Keyboard value='U' onClick={() => this.handleValue("U")} />
                            <Keyboard value='I' onClick={() => this.handleValue("I")} />
                            <Keyboard value='O' onClick={() => this.handleValue("O")} />
                            <Keyboard value='P' className='bnt-cpf-last' onClick={() => this.handleValue("P")} />
                        </Grid >
                        <Grid cols='11 11' className="bg-itens-pedido-carrinho div-segunda-coluna-teclado" >
                            <Keyboard value='A' className='btn-cliente' onClick={() => this.handleValue("A")} />
                            <Keyboard value='S' onClick={() => this.handleValue("S")} />
                            <Keyboard value='D' onClick={() => this.handleValue("D")} />
                            <Keyboard value='F' onClick={() => this.handleValue("F")} />
                            <Keyboard value='G' onClick={() => this.handleValue("G")} />
                            <Keyboard value='H' onClick={() => this.handleValue("H")} />
                            <Keyboard value='J' onClick={() => this.handleValue("J")} />
                            <Keyboard value='K' onClick={() => this.handleValue("K")} />
                            <Keyboard value='L' onClick={() => this.handleValue("L")} />
                        </Grid >
                        <Grid className="bg-itens-pedido-carrinho" >
                            <div className="text-center bnt-teclado bnt-teclado-icones btn-cliente">
                                {/* <img src={require('../../../common/images/Teclado/btn_shift.png')} className="btn-shift" alt="Shift" /> */}
                            </div>
                            <Keyboard value='Z' onClick={() => this.handleValue("Z")} />
                            <Keyboard value='X' onClick={() => this.handleValue("X")} />
                            <Keyboard value='C' onClick={() => this.handleValue("C")} />
                            <Keyboard value='V' onClick={() => this.handleValue("V")} />
                            <Keyboard value='B' onClick={() => this.handleValue("B")} />
                            <Keyboard value='N' onClick={() => this.handleValue("N")} />
                            <Keyboard value='M' onClick={() => this.handleValue("M")} />
                            <div className="text-center bnt-teclado bnt-teclado-icones bnt-cpf-last" onClick={() => this.handleBack()} >
                                <img src={require('../../../common/images/Teclado/btn_backspace.png')} className="btn-shift" alt="Backspace" />
                            </div>
                        </Grid >
                        <Grid className="bg-itens-pedido-carrinho" >
                            <div className="text-center bnt-teclado bnt-teclado-espaco" onClick={() => this.handleValue(" ")}>
                                <img src={require('../../../common/images/Teclado/btn_space.png')} className="btn-space" alt="Espace" />
                            </div>
                        </Grid >
                    </div>
                </div>
            </div>
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
        changeClientNameAction,
        changeCouponAction,
        changeScreenAction,
        changeTextTop
    }, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(BKeyboard)