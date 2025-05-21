import React, { Component } from 'react'
import SaleSummaryScreenRenderer from './sale-summary-screen-renderer'
import StaticConfigPropTypes from '../../../prop-types/StaticConfigPropTypes'
import MessageBusPropTypes from '../../../prop-types/MessageBusPropTypes'
import OrderPropTypes from '../../../prop-types/OrderPropTypes'

class SaleSummaryScreen extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    return <SaleSummaryScreenRenderer {...this.props}/>
  }
}

SaleSummaryScreen.propTypes = {
  msgBus: MessageBusPropTypes,
  staticConfig: StaticConfigPropTypes,
  order: OrderPropTypes
}

export default (SaleSummaryScreen)
