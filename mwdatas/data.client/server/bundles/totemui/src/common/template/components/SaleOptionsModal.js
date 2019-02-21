
import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { NAME_CLIENT, COUPON, COUPON_KEYBOARD, NAME_SCREEN, PAYMENT_SCREEN, BASE_URL } from '../../constants'

const buttonStyle = {
    color: '#3a1b0a'
}

// Retorna as classes da página de seleção de opçao de consumo
export class SaleOptionsModal extends Component {
    getSize(size) {
        return {
            "S": "PEQUENO",
            "M": "MÉDIO",
            "L": "GRANDE"
        }[size] || ""
    }

    renderOptions(allOptions) {
        let colClass = "col-sm-6 col-md-6"
        let isCombo = true
        let hideProdName = false
        if (allOptions[0].size !== null) {
            if (allOptions.length > 2){
                colClass = "col-sm-4 col-md-4"
            }
            isCombo = false
            hideProdName = true
        }
        return _.map(allOptions, (button, index) => {
            return (
                <div className={colClass} key={index} >
                    <div className={`text-center box-produto-modal produto-modal-${!this.props.selected && index == 0 ? 'ativo' : !this.props.selected ? 'inativo' : this.props.selected.partCode === button.partCode ? 'ativo' : 'inativo'}`} onClick={() => this.props.onOptionClick(button)}>
                        <div className="font-index" style={buttonStyle}>
                            {hideProdName ? null : <center className=" align-center titulo-produto-top" >{button.localizedName}</center>}
                        </div>
                        <div style={{ width: "150px", height: "150px", display: "block", margin: "auto", position: "relative" }}>
                            <img src={BASE_URL + button.imageUrl} className="width-produto width-produto-pop-up" alt="bg" />
                        </div>
                        <div className="font-index" style={buttonStyle} style={{ paddingTop: "15px" }}>
                            <p className="titulo-produto-modal align-center">
                                {button.partType == 'Combo' ? 'COMBO' : isCombo ? 'INDIVIDUAL' : this.getSize(button.size)}
                            </p>
                            <p className="titulo-produto-modal align-center">
                                {button.defaultPrice ? 'R$ ' + Number(button.defaultPrice).toLocaleString(this.props.strings.LOCALE, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : ''}
                            </p>
                        </div>
                    </div>
                </div>
            )
        })
    }

    render() {
        if (!this.props.show) {
            return null
        }

        const allOptions = this.props.options
        let msgErro = null

        if (!allOptions || allOptions.length == 0) {
            msgErro = (
                <center>
                    <p style={{ color: "black", fontSize: '30px', fontFamily: 'fonteBK', paddingTop: '100px' }}>
                        OPÇÕES NÃO CADASTRADAS
                    </p>
                </center>
            )
        }

        const is_size = allOptions[0].size !== null
        return (
            <div className="modal show" tabIndex="-1" role="dialog" data-backdrop="static" data-keyboard="false" aria-labelledby="myModalLabel" style={{ backgroundColor: "rgba(100,100,100,0.6)" }}>
                <div className="vertical-alignment-helper">
                    <div className="modal-dialog vertical-align-center">
                        <div className="modal-selecao modal-content">
                            <div className="bg-modal">
                                <div className="bg-modal-int" >
                                    <div className="modal-header">
                                        <div className="max-width row">
                                            <div className="form-inline">

                                                <div className="col-sm-10 col-md-8 text-left">
                                                    <h4 className="modal-title">{is_size ? "ESCOLHA O TAMANHO" : this.props.strings.SELECT_OPTION}</h4>
                                                </div>

                                                <div className="col-sm-2 col-md-4">
                                                    <div style={{ marginLeft: '20px' }} className="close-modal" onClick={() => this.props.onClose()}></div>
                                                </div>

                                            </div>
                                        </div>
                                    </div>
                                    <div className="modal-body">
                                        <div className="max-width row-produto-modal row" style={{ marginTop: is_size ? 0 : "7px" }}>
                                            {msgErro ? msgErro : this.renderOptions(allOptions)}
                                        </div>
                                        {!msgErro &&
                                            <div className="max-width row" style={{ marginTop: "50px" }}>
                                                <div className="text-center col-sm-12 col-md-12">
                                                    <div className={'btn-modal btn-modal-products btn-modal-ativo'} onClick={() => this.props.onConfirm()} >
                                                        <p><span className="btn-modal-text text-line-height">{this.props.strings.CONFIRM}</span></p>
                                                    </div>
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
        )
    }
}

function mapStateToProps(state) {
    return {
        strings: state.strings
    }
}

export default connect(mapStateToProps)(SaleOptionsModal)