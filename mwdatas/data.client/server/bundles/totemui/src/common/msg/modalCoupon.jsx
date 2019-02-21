import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import ReactLoading from 'react-loading'
import { changeSubScreenAction, changeTextTop, registerProductAction, changeScreenAction, setCouponDataAction, selectMenuCategoryAction, changeCouponAction } from '../../actions'
import { PRODUCT_SCREEN, SALE_SCREEN, BASE_URL, COUPON_SCREEN } from '../../common/constants'

export class ModalCoupon extends Component {

    constructor(props) {
        super(props)
    }

    handleCloseModal = () => {
        if (this.props.onClose) {
            this.props.onClose()
        }
    }

    handleConfirmModal = () => {
        if (this.props.cupom.productOptions.length == 1) {
            this.props.registerProductAction(this.props.cupom.productOptions[0].productCode);
            this.props.changeScreenAction(SALE_SCREEN);
            this.props.changeSubScreenAction(PRODUCT_SCREEN);
        } else {
            this.props.setCouponDataAction(this.props.cupom.productOptions)
            // this.props.selectMenuCategoryAction(-1)
            this.props.changeScreenAction(SALE_SCREEN);
            this.props.changeSubScreenAction(COUPON_SCREEN);
        }

        this.props.changeCouponAction("")
        this.props.changeTextTop(this.props.cupom.localizedName);
        this.handleCloseModal();

    }

    handlerModal = () => {
        return (
            <div className={`modal ${this.props.showModal ? 'show' : "fade"}`} id="modalCoupon" tabIndex="-1" role="dialog" data-backdrop="static" data-keyboard="false" aria-labelledby="myModalLabel" style={{ backgroundColor: "rgba(100,100,100,0.6)" }}>
                <div className="vertical-alignment-helper">
                    <div className="modal-dialog vertical-align-center">
                        <div id="bodyModal" className="modal-selecao modal-content">
                            <div className="bg-modal">
                                <div className="bg-modal-int">
                                    <div className="modal-header">
                                        <div className="max-width row">
                                            <div className="form-inline">
                                                <div className="col-sm-10 col-md-8">
                                                    <h4 className="modal-title" style={{marginTop: "0px"}}>{this.props.strings.COUPON_QUESTION}</h4>
                                                </div>
                                                <div className="col-sm-2 col-md-4">
                                                    <div className="close close-modal" onClick={this.handleCloseModal} ></div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="modal-body">
                                        <div className="row" style={{paddingTop:"9px"}}>
                                            <div className="col-sm-6 col-md-6 ">
                                                <div className="img-cupom-popup">
                                                    <img src={BASE_URL + this.props.cupom.imageUrl} className="size-product-coupon" alt="product" />
                                                </div>
                                            </div>
                                            <div className="col-sm-6 col-md-6" style={{paddingTop:"57px"}}>
                                                <div className="font-index font-cupom-popup">
                                                    <span>{this.props.cupom.localizedName}</span>
                                                </div>
                                                {/*<div className="font-index">
                                                    <span className="font-cupom-popup-valor">{`R$ ${(parseFloat(this.props.cupom.price)).toLocaleString(this.props.strings.LOCALE, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}</span>
                                                </div>*/}
                                            </div>
                                        </div>
                                        <div className="max-width">
                                            <div className="col-sm-12 col-md-12 btn-cupom-text">
                                                <div className="col-sm-6 col-md-6 text-left">
                                                    <div className="btn-cupom-popup text-center">
                                                        <span className="text-btn-resumo" onClick={this.handleCloseModal} >{this.props.strings.CANCEL}</span>
                                                    </div>
                                                </div>
                                                <div className="col-sm-6 col-md-6 text-left">
                                                    <div className="btn-cupom-popup-ok text-center">
                                                        <span className="text-btn-resumo" onClick={this.handleConfirmModal} >{this.props.strings.CONFIRM}</span>
                                                    </div>
                                                </div>
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

    render() {

        if (!this.props.cupom) {
            return null
        }

        return (this.handlerModal())
    }
}

function mapStateToProps(state) {
    return {
        cupom: state.order.coupon,
        strings: state.strings
    }
}

function mapDispatchToProps(dispatch) {
    return bindActionCreators({
        changeSubScreenAction,
        registerProductAction,
        changeScreenAction,
        setCouponDataAction,
        selectMenuCategoryAction,
        changeTextTop,
        changeCouponAction
    }, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(ModalCoupon)

