import React from 'react'
import { connect } from 'react-redux'
import { DIALOG_CLOSED } from '3s-posui/constants/actionTypes'


function mapDispatchToProps(dispatch) {
  return {
    closeDialog: function (payload) {
      dispatch({ type: DIALOG_CLOSED, payload: payload })
    }
  }
}

function withCloseDialog(ComponentClass) {
  return connect(null, mapDispatchToProps)(
    function WithCloseDialog(props) {
      return (<ComponentClass {...props}/>)
    })
}

export default withCloseDialog
