import React, { Component } from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { changeScreenAction, changeCpfAction } from '../../actions'
import { PAYMENT_SCREEN, NAME_SCREEN, SALE_SCREEN } from '../constants'


export class ModalCpf extends Component {
    constructor(props) {
        super(props);
        this.state = { cpf: "", msgErro: "", cpfValid: false }
    }

    handleCloseModal = () => {
        if (this.props.onClose) {
            this.props.onClose()
        }
    }

    handleValue(value) {
        if (this.state.cpf.length < 11) {
            this.isValidCPF(this.state.cpf + value)
            this.setState({ cpf: this.state.cpf + value })
        }
    }

    handleBack() {
        const value = this.state.cpf
        this.setState({ cpf: value.substr(0, value.length - 1), msgErro: '', cpfValid: false })
    }

    handleNamehOrder = () => {
        this.props.changeScreenAction(NAME_SCREEN)
    }

    renderFormattedCPF = () => {
        return _.padEnd(this.state.cpf, 11, '_').replace(/(.{3})(.{3})(.{3})(.{2}).*/g, '$1.$2.$3-$4')
    }

    handleCPF = () => {
        this.props.changeCpfAction(this.state.cpf)
        this.props.changeScreenAction(NAME_SCREEN)
    }

    isEqual(strCPF) {
        switch (strCPF) {
            case '00000000000':
            case '11111111111':
            case '22222222222':
            case '33333333333':
            case '44444444444':
            case '55555555555':
            case '66666666666':
            case '77777777777':
            case '88888888888':
            case '99999999999':
                return true
            default:
                return false
        }
    }

    isValidCPF(strCPF) {
        // based on http://www.receita.fazenda.gov.br/aplicacoes/atcta/cpf/funcoes.js
        if (strCPF.length < 11) {
            this.setState({ msgErro: '', cpfValid: false })
            return false
        }
        let Soma = 0;
        for (let i = 1; i <= 9; i++) {
            Soma = Soma + parseInt(strCPF.substring(i - 1, i)) * (11 - i);
        }
        let Resto = (Soma * 10) % 11;
        if ((Resto == 10) || (Resto == 11)) {
            Resto = 0;
        }
        if (Resto != parseInt(strCPF.substring(9, 10))) {
            this.setState({ msgErro: 'CPF INVÁLIDO', cpfValid: false })
            return false;
        }
        Soma = 0;
        for (let i = 1; i <= 10; i++) {
            Soma = Soma + parseInt(strCPF.substring(i - 1, i)) * (12 - i);
        }
        Resto = (Soma * 10) % 11;
        if ((Resto == 10) || (Resto == 11)) {
            Resto = 0;
        }
        if (Resto != parseInt(strCPF.substring(10, 11))) {
            this.setState({ msgErro: 'CPF INVÁLIDO', cpfValid: false })
            return false;
        }


        if (this.isEqual(strCPF)) {
            this.setState({ msgErro: 'CPF INVÁLIDO', cpfValid: false })
            return false;
        }

        this.setState({ msgErro: '', cpfValid: true })
    }

    handleModal = () => {
        return (
            <div className={`modal ${this.props.showModal ? 'show' : "fade"}`} id="modalCPF" tabIndex="-1" role="dialog" data-backdrop="static" data-keyboard="false" aria-labelledby="myModalLabel" style={{ backgroundColor: "rgba(100,100,100,0.6)" }}>
                <div className="vertical-alignment-helper">
                    <div className="modal-dialog vertical-align-center">
                        <div id="bodyModal" className="modal-selecao modal-content">
                            <div className="bg-modal">
                                <div className="bg-modal-int-cpf">
                                    <div className="modal-header">
                                        <div className="max-width row">
                                            <div className="form-inline">

                                                <div className="col-sm-10 col-md-8 text-left">
                                                    <h4 className="modal-title-cpf">{this.props.strings.ORDER_PAYMENT}</h4>
                                                </div>
                                                <div className="col-sm-2 col-md-4" onClick={this.handleCloseModal} >
                                                    <div className="close close-modal"></div>
                                                </div>

                                            </div>
                                        </div>
                                    </div>

                                    <div className="modal-body">
                                        <div className="max-width row" style={{ marginTop: "35px" }}>
                                            <div className="col-sm-12 col-md-12 ">
                                                <p className="titulo-produto">{this.props.strings.ASK_FOR_CPF}</p>
                                            </div>

                                            <div className="col-sm-12 col-md-12 ">
                                                <div className="bg-input-cpf">
                                                    <span className="text-btn-resumo titulo-produto text-line-height">{this.renderFormattedCPF()}</span>
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
                                                    <img src={require('../../common/images/NOTA-FISCAL-CPF/seta_CPF.png')} className="btn-arrow-back" alt="Shift" onClick={() => this.handleBack()} />
                                                </div>
                                            </div>

                                        </div>

                                        <div className="max-width row" style={{ minHeight: '52px' }}>
                                            <p className="font-index text-msg-error">{this.state.msgErro}</p>
                                        </div>

                                        <div className="col-sm-12 col-md-12">
                                            <div className="row">
                                                <div className="col-sm-6 col-md-6 text-left no-padding">
                                                    <div className="btn-nao-modal text-center">
                                                        <span className="text-btn-cpf" onClick={this.handleNamehOrder}>{this.props.strings.CANCEL_SUGGESTION}</span>
                                                    </div>

                                                </div>
                                                {this.state.cpfValid &&
                                                    <div className="col-sm-6 col-md-6 text-left no-padding">
                                                        <div className="btn-confirmar-modal text-center">
                                                            <span className="text-btn-cpf" onClick={this.handleCPF} >{this.props.strings.CONFIRM_CPF}</span>
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
        )

    }

    render() {
        return (<div> {this.handleModal()} </div>
        )
    }

}


function mapStateToProps(state) {
    return {
        selectedScreen: state.selectedScreen,
        modalState: state.modalState,
        strings: state.strings
    }
}

function mapDispatchToProps(dispatch) {
    return bindActionCreators({
        changeScreenAction,
        changeCpfAction
    }, dispatch)
}


export default connect(mapStateToProps, mapDispatchToProps)(ModalCpf)
