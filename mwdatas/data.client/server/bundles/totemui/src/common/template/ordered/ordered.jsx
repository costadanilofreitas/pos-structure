import React, { Component } from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import Header from './header'
import Footer from './footer'
import ProductScreen from './ProductScreen'
import SuggestionScreen from './SuggestionScreen'
import CouponOptionScreen from './CouponOptionScreen'
import MainPayment from '../payment/mainPayment'
import BKeyboard from '../components/BKeyboard'
import FooterKeyboard from '../components/FooterKeyboard'
import FooterNameClient from '../payment/footerNameClient'
import PaymentForm from '../payment/paymentForm'
import { SALE_SCREEN, PAYMENT_SCREEN, NAME_SCREEN, PRODUCT_SCREEN, SUGGESTION_SCREEN, PAYMENT_FORM_SCREEN, COUPON_KEYBOARD, CUSTOMIZE_SCREEN, COUPON_SCREEN } from '../../constants'
import SaleScreen from './SaleScreen'

export class Ordered extends Component {
    constructor(props) {
        super(props)
    }

    renderSelectedScreen = () => {
        switch (this.props.selectedScreen) {
            case SALE_SCREEN:
                switch (this.props.selectedSubScreen) {
                    case PRODUCT_SCREEN:
                        return <ProductScreen />
                    case SUGGESTION_SCREEN:
                        return <SuggestionScreen />
                    case COUPON_SCREEN:
                        return <CouponOptionScreen />
                    default:
                        return <SaleScreen />
                }
            case PAYMENT_SCREEN:
                return <MainPayment />
            case NAME_SCREEN:
                return <BKeyboard subtitle='1' screen={NAME_SCREEN} />
            case PAYMENT_FORM_SCREEN:
                return <PaymentForm />
            case COUPON_KEYBOARD:
                return <BKeyboard subtitle='2' numericKeyboard="true" screen={COUPON_KEYBOARD} />
            default:
                return null
        }
    }

    renderFooter = () => {
        switch (this.props.selectedScreen) {
            case NAME_SCREEN:
            case COUPON_KEYBOARD:
                return <FooterKeyboard />
            case PAYMENT_FORM_SCREEN:
                return null
            default:
                return <Footer />
        }
    }

    render() {
        return (

            <div id="page-ordered">
                <Header />
                {this.renderSelectedScreen()}
                {this.renderFooter()}
            </div>
        )
    }
}

function mapStateToProps(state) {
    return {
        selectedScreen: state.selectedScreen,
        selectedSubScreen: state.selectedSubScreen
    }
}

export default connect(mapStateToProps)(Ordered)