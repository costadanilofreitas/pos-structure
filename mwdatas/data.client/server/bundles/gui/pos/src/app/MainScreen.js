import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { FunctionScreen, SaleScreen, TenderScreen, SignInScreen, RecallScreen } from '.'
import { MENU_DASHBOARD, MENU_ORDER, MENU_PAYMENT, MENU_MANAGER, MENU_SAVED_ORDERS } from '../reducers/menuReducer'

class MainScreen extends PureComponent {

  render() {
    const { currentMenu } = this.props

    switch (currentMenu) {
    case MENU_ORDER:
      return (
        <SaleScreen />
      )
    case MENU_PAYMENT:
      return (
        <TenderScreen />
      )
    case MENU_MANAGER:
      return (
        <FunctionScreen />
      )
    case MENU_SAVED_ORDERS:
      return (
        <RecallScreen />
      )
    case MENU_DASHBOARD:
    default:
      return (
        <SignInScreen />
      )
    }
  }
}

MainScreen.propTypes = {
  /**
   * currentScreen state from `currentScreenReducer`
   */
  currentMenu: PropTypes.number
}

function mapStateToProps({ currentMenu }) {
  return {
    currentMenu
  }
}

export default connect(mapStateToProps)(MainScreen)
