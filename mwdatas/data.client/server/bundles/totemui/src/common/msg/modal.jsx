import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'


const styleSheet = {
    position: "absolute",
    top: "226px"
}
const styleSheetLowerButton = {
    position: "absolute",
    top: "280px"
}

export class Modal extends Component {

    handleCloseModal = () => {
        if (this.props.onClose) {
            this.props.onClose();
        }
    }
    handleConfirmModal = () => {
        if (this.props.onConfirm) {
            this.props.onConfirm();
        }
        this.handleCloseModal();
    }

    handleCancelModal = () => {
        if (this.props.onCancel) {
            this.props.onCancel();
        }
        this.handleCloseModal();
    }

    render() {
        return (
            <div className={`modal ${this.props.showModal ? 'show' : 'fade'}`} id="modal" tabIndex="-1" role="dialog" data-backdrop="static" data-keyboard="false" aria-labelledby="myModalLabel" style={{ backgroundColor: "rgba(100,100,100,0.6)" }}>
                <div className="vertical-alignment-helper">
                    <div className="modal-dialog vertical-align-center">
                        <div id="bodyModal" className="modal-selecao modal-content">
                            <div className="bg-modal">
                                <div className="bg-modal-int">

                                    <div className="modal-header">
                                        <div className="max-width row">
                                            <div className="form-inline">

                                                <div className="col-sm-10 col-md-8 text-left">
                                                    {/* <h4 className="modal-title titulo-produto">{this.props.titleHeader}</h4> */}
                                                    {this.props.showCancel ?
                                                    <h4 className="modal-title">{this.props.strings.CANCELLATION_ORDER}</h4>
                                                    :
                                                    <h4 className="modal-title">{this.props.strings.WARNING}</h4>
                                                    }
                                                </div>
                                                <div className="col-sm-2 col-md-4">
                                                    <div className="close close-modal" onClick={this.handleCloseModal}></div>
                                                </div>

                                            </div>
                                        </div>
                                    </div>

                                    <div className="modal-body">
                                        <div className="max-width row">
                                            <div className="col-sm-12 col-md-12">
                                                <div className="font-index text-center" style={{ color: '#3a1b0a' }}>
                                                    <p className="titulo-produto titulo-body-modal">
                                                        <span>{this.props.titleBody}</span>
                                                    </p>
                                                </div>
                                            </div>

                                            <div id="divcentro" className="col-sm-12 col-md-12 ">
                                                <p className="font-index titulo-modal text-line-height" style={{ paddingTop: '16px' }}>{this.props.divCenter}</p>
                                            </div>
                                        </div>
                                        <div className="max-width" style={this.props.lowerButton ? styleSheetLowerButton : styleSheet}>
                                            {this.props.showCancel ?
                                                <div className="col-sm-12 col-md-12 btn-cupom-popup-text">
                                                    <div className="col-sm-6 col-md-6 text-left">
                                                        <div className="btn-cancelar-transacao-not text-center" onClick={this.handleCancelModal}>
                                                            {/* <div className="btn-cupom-popup text-center" onClick={this.handleCancelModal}>
                                                                <span className="text-btn-resumo-acentuacao">{this.props.cancelButtonText || this.props.strings.CANCEL}</span> */}
                                                        </div>
                                                    </div>
                                                    <div className="col-sm-6 col-md-6 text-left">
                                                        <div className="btn-cancelar-transacao-yes text-center" onClick={this.handleConfirmModal}>
                                                            {/* <div className="btn-cupom-popup-ok text-center" onClick={this.handleConfirmModal}>
                                                            <span className="text-btn-resumo-acentuacao">{this.props.okButtonText || this.props.strings.OK}</span> */}
                                                        </div>
                                                    </div>
                                                </div>
                                                :
                                                <div className="text-center col-sm-12 col-md-12">
                                                    <div className={`btn-modal-ok btn-modal-ativo`} onClick={() => this.handleConfirmModal()}>
                                                        <p> <span className="btn-modal-ok-text text-line-height">{this.props.strings.OK}</span></p>
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
        )
    }
}

function mapStateToProps(state) {
    return {
        strings: state.strings
    }
}

export default connect(mapStateToProps)(Modal)

