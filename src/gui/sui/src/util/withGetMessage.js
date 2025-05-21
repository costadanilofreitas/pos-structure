import React from 'react'
import { connect } from 'react-redux'

import { I18N } from '3s-posui/core'
import { getMessage } from '3s-posui/utils'


function mapStateToProps({ locale }) {
  return {
    messages: locale.messages || {}
  }
}

function withGetMessage(ComponentClass) {
  return connect(mapStateToProps)(
    function WithGetMessages(props) {
      return (<ComponentClass getMessage={(label, values) => {
        return getMessage(props.messages, <I18N id={label} values={values}/>)
      }} {...props}/>)
    })
}

export default withGetMessage
