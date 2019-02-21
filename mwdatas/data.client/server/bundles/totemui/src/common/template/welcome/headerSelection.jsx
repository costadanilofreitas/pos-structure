import React, { Component } from 'react'
import LogoMain from '../../../common/images/BK_Fundo Branco_home.png';


export default class headerSelection extends Component {

    render() {
        return (
            <header className="row no-margin-bottom">
                <img src={LogoMain} alt="Logo" className="logo"></img>
                <div className="text-header font-index font-inicio font-inicio-selection">
                    <p style={{ color: '#eeaa03' }}>VAI COMER</p>
                    <p style={{ color: '#d52b1e' }}>AQUI NA LOJA</p>
                    <p style={{ color: '#3a1b0a' }}>OU VAI LEVAR?</p>
                </div>
            </header>
        )
    }
}