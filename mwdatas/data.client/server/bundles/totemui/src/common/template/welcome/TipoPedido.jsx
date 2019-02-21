import React, { Component } from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import IconLoja from '../../../common/images/icon_loja.png';
import IconViagem from '../../../common/images/icon_viagem.png';
import ModalError from '../../../common/msg/modalError'
import { DINE_IN, TAKE_OUT, SALE_SCREEN, MAIN_SCREEN } from '../../constants'
import { errorAction, changeScreenAction, changeSubScreenAction, saleStartAction, typeChangedAction, changeTextTop, categoryAllAction, selectMenuCategoryAction, productInCategoryAction } from '../../../actions'


export class TipoPedido extends Component {
    handleButtonClick = (saleType) => {
        const totemId = window.location.hash.split('#')[1]
        if (totemId) {
            this.props.saleStartAction(totemId, 'pt-br', saleType).then((data) => {
                if (data.payload.message) {
                    this.props.errorAction(data)
                }

                this.props.typeChangedAction(saleType)
                this.props.changeScreenAction(SALE_SCREEN)
                this.props.changeSubScreenAction(MAIN_SCREEN)
                this.props.changeTextTop(this.props.strings.CHOOSE_HERE)

                this.props.categoryAllAction().then((result) => {
                    const categoria0 = result.payload.data[0]
                    this.props.selectMenuCategoryAction(categoria0)
                    this.props.productInCategoryAction(categoria0.id)
                })
            })
        }
    }

    render() {
        return (
            <div className="max-width row no-margin-botoon text-center imgpos">
                <div className="form-inline" style={{ marginTop: '50px' }}>
                    <div className="form-group box-selecao box-selecao-loja" onClick={() => this.handleButtonClick(DINE_IN)}>
                        <img src={IconLoja} alt="Loja" className="img-loja" />
                        <p className="font-index font-btn-escolha">{this.props.strings.EAT_IN}</p>
                    </div>
                    <div className="form-group box-selecao" onClick={() => this.handleButtonClick(TAKE_OUT)}>
                        <img src={IconViagem} alt="Viagem" className="img-viagem" />
                        <p className="font-index font-btn-escolha">{this.props.strings.TAKE_OUT}</p>
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

function mapDispatchToProps(dispatch) {
    return bindActionCreators({
        errorAction,
        changeScreenAction,
        changeSubScreenAction,
        saleStartAction,
        typeChangedAction,
        changeTextTop,
        categoryAllAction,
        selectMenuCategoryAction,
        productInCategoryAction
    }, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(TipoPedido)