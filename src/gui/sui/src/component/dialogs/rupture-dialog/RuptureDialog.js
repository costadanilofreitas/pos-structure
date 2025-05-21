import React, { Component } from 'react'
import RuptureDialogRenderer from './rupture-dialog-renderer'
import MessageBusPropTypes from '../../../prop-types/MessageBusPropTypes'
import WelcomeScreen from '../../../app/screen/welcome-screen/WelcomeScreen'


class RuptureDialog extends Component {
  render() {
    return <RuptureDialogRenderer{...this.props}/>
  }
}

WelcomeScreen.propTypes = {
  msgBus: MessageBusPropTypes
}

export default (RuptureDialog)
