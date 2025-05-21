import React, { Component } from 'react'
import PropTypes from 'prop-types'
import LoginInfoRenderer from './login-info-renderer'
import MessageBusPropTypes from '../../../prop-types/MessageBusPropTypes'
import { getBusinessDate } from '../../../util/dateHelper'
import WorkingModePropTypes from '../../../prop-types/WorkingModePropTypes'
import OperatorPropTypes from '../../../prop-types/OperatorPropTypes'
import PosStatePropTypes from '../../../prop-types/PosStatePropTypes'
import { operatorIsInState } from '../../util/operatorValidator'
import { isLoginQS } from '../../model/modelHelper'

export default class LoginInfo extends Component {
  constructor(props) {
    super(props)

    this.onLogin = this.onLogin.bind(this)
  }

  render() {
    const { posState, operator, workingMode } = this.props
    if (posState == null || posState.id == null || posState.storeId == null) {
      return null
    }

    if (operator == null) {
      return null
    }

    if (workingMode == null || workingMode.podType == null) {
      return null
    }

    let operatorId = null
    let operatorName = null
    if ((operatorIsInState(operator, 'PAUSED') && isLoginQS(workingMode)) || operatorIsInState(operator, 'LOGGEDIN')) {
      operatorId = operator.id
      operatorName = operator.name
    }

    let businessPeriod = null
    if (posState.period != null) {
      businessPeriod = getBusinessDate(posState.period)
      if (isNaN(businessPeriod.getTime())) {
        businessPeriod = null
      }
    }

    return (
      <LoginInfoRenderer
        posNumber={posState.id}
        workingMode={workingMode}
        storeCode={posState.storeId}
        currentDate={this.props.getCurrentDate()}
        businessDate={businessPeriod}
        operatorId={operatorId}
        operatorName={operatorName}
        onLogin={this.onLogin}
      />
    )
  }

  onLogin() {
    if (this.props.operator.state === 'LOGGEDIN') {
      this.props.messageBus.syncAction('logoffuser')
    } else {
      this.props.messageBus.syncAction('common_login')
    }
  }
}

LoginInfo.propTypes = {
  posState: PosStatePropTypes,
  operator: OperatorPropTypes,
  workingMode: WorkingModePropTypes,
  getCurrentDate: PropTypes.func,
  messageBus: MessageBusPropTypes,
  businessDate: PropTypes.object
}
