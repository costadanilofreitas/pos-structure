import { connect } from 'react-redux'
import React from 'react'
import { bindActionCreators } from 'redux'
import { showInfoMessageAction } from '3s-posui/actions'


function mapDispatchToProps(dispatch) {
  return bindActionCreators({
    showInfoMessageAction
  }, dispatch)
}

function withShowInfoMessage(ComponentClass) {
  return connect(null, mapDispatchToProps)(
    function WithShowInfoMessage(props) {
      return (<ComponentClass showInfoMessage={showInfoMessageAction} {...props}/>)
    })
}

export default withShowInfoMessage
