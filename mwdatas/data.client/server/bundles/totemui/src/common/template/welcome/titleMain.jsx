import React, { Component } from 'react';
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import axios from 'axios'
import Shape from '../../../common/images/Shape_1.png';
import Header from './headerMain'
import { TYPE_SELECT_SCREEN, REQUEST_URL } from '../../constants'
import { changeScreenAction } from '../../../actions'

const mainDivStyle = {
    height: "100vh",
    width: "100vw",
    overflow: "hidden"
}

const parentDivStyle = {
    width: "100vw",
    height: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    overflow: "hidden"
}


export class TitleMain extends Component {
    constructor(props) {
        super(props)
        this.state = {
            image: null
        }
    }
    componentWillMount() {
        const totemId = window.location.hash.split('#')[1]
        this.setState({image: ""})
        axios.get(`${REQUEST_URL}banner/mainScreen/${totemId}`)
        .then((resp) => {
            this.setState({image: resp.data})
        })
        .catch((error) => {
            this.setState({image: null})
        })
    }
    handleClick = () => {
        this.props.changeScreenAction(TYPE_SELECT_SCREEN)
    }
    render() {
        let paddingBandeiras = '20px'
        if (this.state.image !== null) {
            return (
                <div style={parentDivStyle}>
                    <div className="row text-center no-margin-bottom" style={mainDivStyle} onClick={this.handleClick} >
                        <img src={this.state.image} />
                    </div>
                </div>
            )
        } else {
            return (
                <div style={parentDivStyle}>
                    <div className="row text-center no-margin-bottom" style={mainDivStyle} onClick={this.handleClick} >
                        <Header />
                        <div className="main-content text-header font-index font-inicio">
                            <p style={{ color: '#eeaa03' }}>NÃO PEGUE FILA.</p>
                            <p style={{ color: '#d52b1e' }}>FAÇA AQUI</p>
                            <p style={{ color: '#3a1b0a' }}>O SEU PEDIDO.</p>
                            <img src={Shape} alt="Barra" className="alinha-meio btn-toque"></img>
                            <span className="txt-toque">TOQUE NA TELA PARA INICIAR</span>
                        </div>

                        <div style={{ paddingTop: "69px" }}>
                            <p style={{ color: "black", fontSize: '30px', fontFamily: 'fonteBK', paddingBottom: '10px' }}>PAGAMENTO SOMENTE EM CARTÃO, NAS BANDEIRAS:</p>

                            <img src={require('../../../common/images/TELA-DE-PAGAMENTO/cartao_visa.png')} style={{width: '70px' }} alt="Visa" />
                            <img src={require('../../../common/images/TELA-DE-PAGAMENTO/cartao_mastercard.png')} style={{width: '70px', paddingLeft: paddingBandeiras }} alt="Marter" />
                            <img src={require('../../../common/images/TELA-DE-PAGAMENTO/cartao_americaexpress.png')} style={{width: '40px', paddingLeft: paddingBandeiras  }} alt="American" />
                            <img src={require('../../../common/images/TELA-DE-PAGAMENTO/cartao_diners.png')} style={{width: '55px', paddingLeft: paddingBandeiras  }} alt="American" />
                            <img src={require('../../../common/images/TELA-DE-PAGAMENTO/cartao_elo.png')} style={{width: '50px', paddingLeft: paddingBandeiras  }} alt="Alen" />
                            <img src={require('../../../common/images/TELA-DE-PAGAMENTO/cartao_alelo.png')} style={{width: '70px', paddingLeft: paddingBandeiras  }} alt="alelo" />
                            <img src={require('../../../common/images/TELA-DE-PAGAMENTO/cartao_ticket.png')} style={{width: '140px', paddingLeft: paddingBandeiras  }} alt="titket" />
                            <img src={require('../../../common/images/TELA-DE-PAGAMENTO/cartao_sodexo.png')} style={{width: '130px', paddingLeft: paddingBandeiras  }} alt="titket" />

                        </div>
                    </div>
                </div>
            )
        }
    }
}

function mapDispatchToProps(dispatch) {
    return bindActionCreators({
        changeScreenAction
    }, dispatch)
}

export default connect(null, mapDispatchToProps)(TitleMain)