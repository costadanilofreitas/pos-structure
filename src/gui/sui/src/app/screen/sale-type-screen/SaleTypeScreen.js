import React, { Component } from 'react'
import PropTypes from 'prop-types'
import SaleTypeScreenRenderer from './sale-type-screen-renderer'
import StaticConfigPropTypes from '../../../prop-types/StaticConfigPropTypes'

class SaleTypeScreen extends Component {
  render() {
    return (
      <SaleTypeScreenRenderer {...this.props}/>
    )
  }
}

SaleTypeScreen.propTypes = {
  staticConfig: StaticConfigPropTypes,
  startKioskOrder: PropTypes.func,
  toggleSaleTypeScreen: PropTypes.func
}

export default SaleTypeScreen
