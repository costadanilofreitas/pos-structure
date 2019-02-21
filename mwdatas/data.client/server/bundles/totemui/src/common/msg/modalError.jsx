import React, { Component } from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { changeScreenAction, saleApagarChangedAction } from '../../actions'
import { PAYMENT_FORM_SCREEN, NAME_SCREEN, SALE_SCREEN } from '../constants'


export class ModalError extends Component {

    constructor(props) {
        super(props);
    }
    componentWillMount() {
        setTimeout(()=>{
            window.location.reload(true);
        }, 5000)
    }
    render() {

        // ERROR
        const { type, menssageCode, code } = this.props.error

        return (
            <div className={'modal show'} tabIndex="-1" role="dialog" data-backdrop="static" data-keyboard="false" aria-labelledby="myModalLabel" style={{ backgroundColor: "rgba(100,100,100,0.6)" }}>
                <div className="vertical-alignment-helper">
                    <div className="modal-dialog vertical-align-center">
                        <div id="bodyModal" className="modal-selecao modal-content">
                            <div className="bg-modal">
                                <div className="bg-modal-int">
                                    <div className="modal-header">
                                        <div className="max-width row">
                                            <div className="form-inline">

                                                <div className="col-sm-10 col-md-8 text-left">
                                                    <h4 className="modal-title-cpf">ERRO</h4>
                                                </div>

                                            </div>
                                        </div>
                                    </div>

                                    <div className="modal-body">
                                        <div className="max-width row">
                                            <div className="col-sm-12 col-md-12 ">
                                                <center>
                                                    <div style={{ marginTop: "50px", marginBottom: '50px' }}>
                                                        <span className="font-index" style={{ fontSize: '30px' }}>OCORREU UM ERRO E<br />O TOTEM SERÁ REINICIADO.<br />POR FAVOR, AGUARDE OU<br />DIRIJA-SE AO BALCÃO.</span>
                                                    </div>

                                                    {/*
                                                    <p style={{ whiteSpace: "pre-line" }}>ERROR: {code}</p>
                                                    <p style={{ whiteSpace: "pre-line" }}>TYPE: {type}</p>
                                                    <p style={{ whiteSpace: "pre-line" }}>{menssageCode}</p>
                                                    */}

                                                </center>

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

}


function mapStateToProps(state) {
    return {
        error: state.error,
    }
}

function mapDispatchToProps(dispatch) {
    return bindActionCreators({

    }, dispatch)
}


export default connect(mapStateToProps, mapDispatchToProps)(ModalError)
