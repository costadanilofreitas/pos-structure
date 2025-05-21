import React from 'react'
import { DIALOGS_CHANGED } from '3s-posui/constants/actionTypes'
import { connect } from 'react-redux'


function mapDispatchToProps(dispatch) {
  return {
    changeDialog: function (payload) {
      dispatch({ type: DIALOGS_CHANGED,
        payload: [
          payload
        ] })
    }
  }
}

function withChangeDialog(ComponentClass) {
  return connect(null, mapDispatchToProps)(
    function WithChangeDialog(props) {
      return (<ComponentClass {...props}/>)
    })
}

export default withChangeDialog
