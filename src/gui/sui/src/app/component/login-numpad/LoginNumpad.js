import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'

import LoginNumpadRenderer from './renderer'
import OperatorPropTypes from '../../../prop-types/OperatorPropTypes'
import { operatorIsInState, operatorIsNotInState } from '../../util/operatorValidator'
import OperatorState from '../../model/OperatorState'
import MessageBusPropTypes from '../../../prop-types/MessageBusPropTypes'
import WorkingModePropTypes from '../../../prop-types/WorkingModePropTypes'
import { posIsInState } from '../../util/posValidator'
import { isLoginQS } from '../../model/modelHelper'


export default class LoginNumpad extends Component {
  constructor(props) {
    super(props)

    this.state = {
      userId: '',
      blockNumpad: false
    }

    this.handleOnLogin = this.handleOnLogin.bind(this)
    this.handleUserIdChange = this.handleUserIdChange.bind(this)
  }

  render() {
    const { operator, workingMode } = this.props
    let showNumPad = true
    let showButton = true
    let blockMessage = null

    if (isLoginQS(workingMode)) {
      showNumPad = operatorIsNotInState(operator, OperatorState.LoggedIn, OperatorState.Paused)
    }

    if (posIsInState(this.props.posState, 'BLOCKED', 'CLOSED')) {
      showNumPad = false
      if (isLoginQS(workingMode)) {
        showButton = operatorIsInState(operator, OperatorState.LoggedIn, OperatorState.Paused)
      } else {
        showButton = false
      }

      if (posIsInState(this.props.posState, 'BLOCKED')) {
        blockMessage = <I18N id="$POS_BLOCKED"/>
      } else {
        blockMessage = <I18N id="$DAY_CLOSE_ALREADY_CLOSED" values={{ 0: this.props.posState.id }}/>
      }
    }

    return (
      <LoginNumpadRenderer
        showNumpad={showNumPad}
        showButton={showButton}
        blockMessage={blockMessage}
        onLogin={this.handleOnLogin}
        userId={this.state.userId}
        onUserIdChange={this.handleUserIdChange}
      />
    )
  }

  handleOnLogin() {
    const hasDialog = this.props.dialogs.length !== 0
    if (hasDialog) {
      return
    }

    this.setState({ blockNumpad: true })

    if (operatorIsNotInState(this.props.operator, OperatorState.LoggedIn, OperatorState.Paused)) {
      if (posIsInState(this.props.posState, 'BLOCKED')) {
        this.props.msgBus.syncAction('common_logoff')
      } else {
        this.props.msgBus.syncAction('common_login', this.state.userId)
      }
    } else if (isLoginQS(this.props.workingMode) || (posIsInState(this.props.posState, 'BLOCKED'))) {
      this.props.msgBus.syncAction('common_logoff')
    } else {
      this.props.msgBus.syncAction('common_login', this.state.userId)
    }

    this.props.msgBus.parallelSyncAction('deselect_table')
    this.setState({ userId: '', blockNumpad: false })
  }

  handleUserIdChange(userId) {
    const maxInputNumbers = 6

    if (this.state.blockNumpad) {
      return
    }

    if (userId.length >= maxInputNumbers + 1) {
      return
    }

    let newText = userId
    const regexOnlyNumbers = /^-?\d*$/

    if (newText.length > this.state.userId.length) {
      if (regexOnlyNumbers.test(newText)) {
        if (this.autoFormat) {
          newText = this.autoFormat(newText)
        }
        this.setState({ userId: newText })
      }
    } else {
      this.setState({ userId: newText })
    }
  }
}

LoginNumpad.propTypes = {
  operator: OperatorPropTypes,
  msgBus: MessageBusPropTypes,
  workingMode: WorkingModePropTypes,
  posState: PropTypes.shape({
    id: PropTypes.string,
    period: PropTypes.string,
    state: PropTypes.string
  }),
  dialogs: PropTypes.array
}
