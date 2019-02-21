import React, { Component } from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { changeScreenAction, saleApagarChangedAction } from '../../actions'
import { PAYMENT_FORM_SCREEN, NAME_SCREEN, SALE_SCREEN } from '../constants'


export class ModalMoneyPartial extends Component {
    constructor(props) {
        super(props);
        this.state = { valueMoney: '', msgErro: '' }
    }

    handleCloseModal = () => {
        if (this.props.onClose){
            this.props.onClose()
        }
    }

    handleValue(value) {
        this.setState({ valueMoney: this.state.valueMoney + value })
    }

    handleBack() {
        const value = this.state.valueMoney
        this.setState({ valueMoney: value.substr(0, value.length - 1) })
    }

    handleCancel = () => {
        if (this.props.onCancel) {
            this.props.onCancel()
        }
    }

    renderFormattedMoney() {
        return 'R$ ' + (Number(this.state.valueMoney)/100.).toLocaleString(this.props.strings.LOCALE, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }

    handleConfirm = () => {
        const value = this.state.valueMoney/100.
        if (this.props.aPagar >= value) {
            // this.props.saleApagarChangedAction(value)
            if (this.props.onConfirm) {
                this.props.onConfirm(value)
            }
        }
    }

    isValidMoney() {
        const amount = Number(this.state.valueMoney)/100.
        if (amount > 0 && amount <= Number(this.props.aPagar)) {
            return true;
        } else {
            return false
        }

    }

    handleModal = () => {
        if (!this.props.showModal) {
            return null
        }
        return (
            <div className="modal show" id="modalCPF" tabIndex="-1" role="dialog" data-backdrop="static" data-keyboard="false" aria-labelledby="myModalLabel" style={{ backgroundColor: "rgba(100,100,100,0.6)" }}>
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
                                            </div>
                                        </div>
                                    </div>

                                    <div className="modal-body" style={{padding: 0}}>
                                        <div className="max-width row" style={{ marginTop: "10px" }}>
                                            <div className="col-sm-12 col-md-12" style={{padding: 0}}>
                                                <p style={{fontSize: '18pt', fontFamily: 'fontebk-DinBold', textAlign: 'center' }}>INSIRA O VALOR DO PAGAMENTO</p>
                                            </div>

                                            <div className="col-sm-12 col-md-12 ">
                                                <div className="bg-input-cpf">
                                                    <span className="text-btn-resumo titulo-produto text-line-height">{this.renderFormattedMoney()}</span>
                                                </div>

                                            </div>
                                            <span className="bg-amount" style={{float: 'left', marginRight: 0}} onClick={()=>this.setState({valueMoney: `${this.props.aPagar*100}`})}><span style={{color: '#94451E'}}>RESTANTE:</span> <span style={{color: 'white'}}>R${Number(this.props.aPagar).toLocaleString(this.props.strings.LOCALE, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span></span>
                                            <span className="bg-amount" style={{float: 'right', marginLeft: 0, width: '50%'}}><span style={{color: '#94451E'}}>TOTAL A PAGAR:</span> <span style={{color: 'white'}}>R${Number(this.props.total).toLocaleString(this.props.strings.LOCALE, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span></span>

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
                                                <div className="text-center bnt-cpf" onClick={()=>this.setState({valueMoney: ''})}>
                                                    <span style={{fontSize: '200%', lineHeight: '200%'}}>LIMPAR</span>
                                                </div>
                                                <div className="text-center bnt-cpf" onClick={() => this.handleValue(0)}>
                                                    <span>0</span>
                                                </div>
                                                <div className="text-center bnt-cpf  bnt-cpf-last">
                                                    <img src={require('../../common/images/NOTA-FISCAL-CPF/seta_CPF.png')} className="btn-arrow-back" alt="Shift" onClick={() => this.handleBack()} />
                                                </div>
                                            </div>

                                        </div>

                                        <div className="col-sm-12 col-md-12">
                                            <div className="row">
                                                <div className="col-sm-6 col-md-6 text-left no-padding">
                                                    <div className="btn-nao-modal text-center">
                                                        <span className="text-btn-cpf" onClick={this.handleCancel}>{this.props.strings.CANCEL}</span>
                                                    </div>

                                                </div>
                                                {this.isValidMoney() ?
                                                    <div className="col-sm-6 col-md-6 text-left no-padding">
                                                        <div className="btn-confirmar-modal text-center" style={{marginLeft: 5}}>
                                                            <span className="text-btn-cpf" onClick={this.handleConfirm} >{this.props.strings.CONFIRM}</span>
                                                        </div>
                                                    </div>
                                                    :
                                                    <div className="col-sm-6 col-md-6 text-left no-padding">
                                                        <div className="text-center" style={{marginLeft: 5}}>
                                                            <span className="text-btn-cpf" style={{color: '#d52b1e'}}>{Number(this.state.valueMoney)/100. > Number(this.props.aPagar) ? "VALOR INVÁLIDO" : ""}</span>
                                                        </div>
                                                    </div>
                                                }

                                            </div>
                                        </div>

                                    </div>
                                    {this.state.msgErro}
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
        saleApagarChangedAction
    }, dispatch)
}


export default connect(mapStateToProps, mapDispatchToProps)(ModalMoneyPartial)
