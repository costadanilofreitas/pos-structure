import React, { Component } from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { EN_LANG, ES_LANG, BR_LANG } from '../../constants'
import { changeLanguageAction } from '../../../actions'
import BandeiraUS from '../../../common/images/bandeira_us.png';
import BandeiraESP from '../../../common/images/bandeira_esp.png';
import BandeiraBR from '../../../common/images/bandeira_br.png';
import BandeiraAcess from '../../../common/images/icon_acessibilidade.png';


export class FooterSelection extends Component {
    
    handleChangeLanguage(lang) {
        this.props.changeLanguageAction(lang)
    }

    render() {
        return (
            <footer className="row no-margin-botton">
                <div className="col-md-2"></div>
                <div className="col-md-8" style={{ marginBottom: "-3.2vh" }}>
                    <p className="font-index font-idioma">{this.props.strings.FOOTER_LANG}</p>
                    <img src={BandeiraUS} alt="US" className="linguagem linguagem-margin" onClick={()=>this.handleChangeLanguage(EN_LANG)} />
                    <img src={BandeiraESP} alt="ESP" className="linguagem linguagem-margin" onClick={()=>this.handleChangeLanguage(ES_LANG)} />
                    <img src={BandeiraBR} alt="BR" className="linguagem" onClick={()=>this.handleChangeLanguage(BR_LANG)} />
                </div>
                <div className="col-md-2">
                    <img src={BandeiraAcess} alt="acessibilidade" className="acessibility" />
                </div>
            </footer>
        )
    }
}

function mapStateToProps(state) {
    return {
        strings: state.strings
    }
}

function mapDispatchToProps(dispatch) {
    return bindActionCreators({
        changeLanguageAction
    }, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(FooterSelection)