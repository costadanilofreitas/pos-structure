import React, { Component } from 'react'
import PropTypes from 'prop-types'

import ConfirmationScreenRenderer from './confirmation-screen-renderer'
import MessageBusPropTypes from '../../../prop-types/MessageBusPropTypes'
import StaticConfigPropTypes from '../../../prop-types/StaticConfigPropTypes'


class ConfirmationScreen extends Component {
  render() {
    return (
      <ConfirmationScreenRenderer
        staticConfig={this.props.staticConfig}
        msgBus={this.props.msgBus}
        startKioskOrder={this.props.startKioskOrder}
        cancelConfirmationScreen={this.props.cancelConfirmationScreen}
      />
    )
  }
}

ConfirmationScreen.propTypes = {
  msgBus: MessageBusPropTypes,
  staticConfig: StaticConfigPropTypes,
  startKioskOrder: PropTypes.func,
  cancelConfirmationScreen: PropTypes.func
}

export default ConfirmationScreen
