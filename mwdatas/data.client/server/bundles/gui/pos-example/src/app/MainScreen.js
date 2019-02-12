import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { FunctionScreen, SaleScreen, TenderScreen, SignInScreen } from '.'

class MainScreen extends Component {

  state = {
    showFunctionScreen: false
  }

  render() {
    const { order } = this.props
    const attributes = order['@attributes'] || {}
    const operatorLogged = this.props.operator.stateCode === '2'
    const { showFunctionScreen } = this.state

    if (showFunctionScreen) {
      return (
        <FunctionScreen
          onExit={() => this.setState({ showFunctionScreen: false })}
        />
      )
    }

    if (!operatorLogged) {
      return (
        <SignInScreen
          onShowFunctionScreen={() => this.setState({ showFunctionScreen: true })}
        />
      )
    }

    switch (attributes.state) {
    case 'TOTALED':
      return (
        <TenderScreen />
      )
    case 'IN_PROGRESS':
    default:
      return (
        <SaleScreen
          onShowFunctionScreen={() => this.setState({ showFunctionScreen: true })}
        />
      )
    }
  }
}

MainScreen.propTypes = {
  /**
   * Order state from `orderReducer`
   */
  order: PropTypes.object,
  /**
   * Operator state from `operatorReducer`
   */
  operator: PropTypes.object
}

MainScreen.defaultProps = {
  order: {},
  operator: {}
}

function mapStateToProps(state) {
  return {
    order: state.order,
    operator: state.operator
  }
}

export default connect(mapStateToProps)(MainScreen)
