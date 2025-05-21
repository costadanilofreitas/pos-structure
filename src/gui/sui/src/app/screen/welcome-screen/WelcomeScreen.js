import React, { Component } from 'react'
import WelcomeScreenRenderer from './welcome-screen-renderer'
import StaticConfigPropTypes from '../../../prop-types/StaticConfigPropTypes'
import MessageBusPropTypes from '../../../prop-types/MessageBusPropTypes'

class WelcomeScreen extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    return <WelcomeScreenRenderer {...this.props}/>
  }
}

WelcomeScreen.propTypes = {
  msgBus: MessageBusPropTypes,
  staticConfig: StaticConfigPropTypes
}

export default (WelcomeScreen)
