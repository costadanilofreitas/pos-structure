import React from 'react'
import { connect } from 'react-redux'

import { MessageBus } from '3s-posui/core'

function mapStateToProps(state) {
  return {
    posId: state.posId
  }
}

function withMessageBus(ComponentClass) {
  return connect(mapStateToProps)(
    function WithMessageBus(props) {
      const msgBus = new MessageBus(props.posId)
      return (<ComponentClass msgBus={msgBus} {...props}/>)
    })
}

export default withMessageBus
