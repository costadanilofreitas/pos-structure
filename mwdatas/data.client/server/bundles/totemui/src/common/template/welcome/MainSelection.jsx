import React, { Component } from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import HeaderMain from './headerMain';
import TipoPedido from './TipoPedido';
import FooterSelection from './footerSelection';


const parentDivStyle = {
    width:"100vw",
    height:"100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center"
}

// Retorna as classes da página de seleção de opçao de consumo
export class MainSelection extends Component {
    render() {
        return (
            <div style={{height:"100vh", width:"100vw"}}>
                <HeaderMain />
                <div className="text-center">
                    <div className="text-header font-index font-inicio">
                        <p style={{ color: '#eeaa03' }}>{this.props.strings.MAIN_SELECTION_TITLE1}</p>
                        <p style={{ color: '#d52b1e' }}>{this.props.strings.MAIN_SELECTION_TITLE2}</p>
                        <p style={{ color: '#3a1b0a' }}>{this.props.strings.MAIN_SELECTION_TITLE3}</p>
                    </div>
                </div>
                <TipoPedido />

            </div>
        )
    }
}

function mapStateToProps(state) {
    return {
        strings: state.strings
    }
}

export default connect(mapStateToProps)(MainSelection)