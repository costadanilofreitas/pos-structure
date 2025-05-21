import React from 'react'
import { connect } from 'react-redux'

import { MessageBus } from '3s-posui/core'
import ExecuteActionMessageBus from './ExecuteActionMessageBus'


function mapStateToProps(state) {
  return {
    posId: state.posId,
    actionRunning: state.actionRunning
  }
}

function withExecuteActionMessageBus(ComponentClass) {
  return connect(mapStateToProps)(
    function WithMessageBus(props) {
      const msgBus = new MessageBus(props.posId)
      const isActionRunning = props.actionRunning.busy === true
      const executeActionMessageBus = new ExecuteActionMessageBus(msgBus, props.dispatch, isActionRunning)
      return (<ComponentClass msgBus={executeActionMessageBus} {...props}/>)
    })
}

export default withExecuteActionMessageBus
