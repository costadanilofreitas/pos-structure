import React, { Component } from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import ImgBtnVoltar from '../../../common/images/icon_voltar.png'
import Logo from '../../../common/images/icon_pedido_bk.png'
import Modal from '../../msg/modal'
import { changeScreenAction, changeSubScreenAction, changeTextTop, saleCancelAction } from '../../../actions'
import { BASE_URL, TYPE_SELECT_SCREEN, SALE_SCREEN, PAYMENT_SCREEN, NAME_SCREEN, PRODUCT_SCREEN, MAIN_SCREEN, SUGGESTION_SCREEN, COUPON_KEYBOARD, TEXT_TOP_MAIN, CUSTOMIZE_SCREEN } from '../../constants'
import Grid from '../../layout/grid'
import _ from 'lodash'

export class Top extends Component {
    constructor(params) {
        super(params);
        this.state = {
            showModal: false
        }
    }

    renderLogoImg() {
        if (_.includes([PRODUCT_SCREEN, SUGGESTION_SCREEN, CUSTOMIZE_SCREEN], this.props.selectedSubScreen)) {
            //return this.props.order.lastItemSold.productComboImg
            // const activeItem = this.props.order.items[this.props.order.activeItem]
            // var test = this.props.productCurrentImg
            return BASE_URL + this.props.productCurrentImg
        }
        return Logo
    }

    handleCancelOrder = () => {
        this.setState({ showModal: true });
    }

    handleCloseModal = () => {
        this.setState({ showModal: false });
    }

    handleConfirmCancelOrder = () => {
        this.props.saleCancelAction(this.props.order.sale_token)
    }

    render() {
        return (
            <div className="row row-ordered" style={{ marginTop: '16px' }}>
                <div className="bg-fundo-topo"></div>
                <Grid cols='0 3 3 ' className="bg-voltar-padd">
                    <div className="bg-voltar text-center"
                        onClick={this.props.cancelOrder ? this.handleCancelOrder : this.props.onGoBack}
                        style={{ marginTop: '20px' }}>
                        <h2 style={{ paddingTop: '19px', paddingLeft: '29px' }}>
                            <img src={ImgBtnVoltar} className="icon_voltar" alt="voltar" style={{ marginRight: '10px' }} />
                            <span className="font-index icon-voltar-text">{this.props.strings.BACK}</span>
                        </h2>
                    </div>
                </Grid>

                <Grid cols='0 6 6' className="titulo-topo font-index" style={{ color: '#d52b1e', height: 100, textAlign: "center", lineHeight: "41px", fontSize: '360%', display: 'flex', alignItems: 'center', justifyContent: 'center' }} >
                    {this.props.title}
                </Grid>

                <Grid cols='0 3 3' className="text-right" >
                    <div style={{ width: "110px", height: "110px", display: "block", margin: "auto", position: "relative" }}>
                        <img src={this.renderLogoImg()} className="width-produto width-produto-top" alt="logo" />
                    </div>
                </Grid>
                <Modal
                    showModal={this.state.showModal}
                    divCenter={this.props.strings.CANCEL_ORDER_CONFIRM}
                    onConfirm={this.handleConfirmCancelOrder}
                    onCancel={this.handleCloseModal}
                    onClose={this.handleCloseModal}
                    okButtonText={this.props.strings.YES}
                    cancelButtonText={this.props.strings.NO}
                    showCancel
                />
            </div>

        )
    }
}

function mapStateToProps(state) {
    return {
        title: state.title,
        selectedScreen: state.selectedScreen,
        selectedSubScreen: state.selectedSubScreen,
        order: state.order,
        strings: state.strings,
        productCurrentImg: state.product.productCurrentImg,
    }
}

function mapDispatchToProps(dispatch) {
    return bindActionCreators({
        changeScreenAction,
        changeSubScreenAction,
        changeTextTop,
        saleCancelAction
    }, dispatch)
}


export default connect(mapStateToProps, mapDispatchToProps)(Top)