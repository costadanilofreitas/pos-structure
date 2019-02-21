import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import IconLoja from '../../../common/images/icon_loja.png';
import IconViagem from '../../../common/images/icon_viagem.png';
import Ordered from '../../../common/template/ordered/ordered'

export default class bodySelection extends Component {
    constructor(props) {
        super(props)
        this.state = { opcaoConsumo: "MEU PEDIDO - PARA COMER NA LOJA" }
    }

    Redirect(event,opcaoConsumo) {
        event.preventDefault();
        //console.log(opcaoConsumo)
        ReactDOM.render(<Ordered Title="ESCOLHA AQUI" opcaoConsumo={opcaoConsumo} />, document.getElementById("app"));
    }

    RedirecLoja(event) {
        event.preventDefault();
        this.Redirect(event,"MEU PEDIDO - PARA COMER NA LOJA")
    }

    RedirecViagem(event) {
        event.preventDefault();
        this.Redirect(event,"MEU PEDIDO - PARA VIAGEM")
    }

    render() {
        return (
            <div className="max-width row text-center imgpos">
                <div className="form-inline">
                    <div className="form-group box-selecao box-selecao-loja" onClick={this.RedirecLoja.bind(this)}>
                        <img src={IconLoja} alt="Loja" className="img-loja" />
                        <p className="font-index font-btn-escolha">LOJA</p>
                    </div>
                    <div className="form-group box-selecao" onClick={this.RedirecViagem.bind(this)}>
                        <img src={IconViagem} alt="Viagem" className="img-viagem" />
                        <p className="font-index font-btn-escolha">VIAGEM</p>
                    </div>
                </div>
            </div>
        )
    }
}