import React from 'react'
import { connect } from 'react-redux'


function mapDispatchToProps(dispatch) {
  return {
    changeMenu: function (payload) {
      dispatch({ type: 'CHANGE_MENU', payload })
    }
  }
}

function withChangeMenu(ComponentClass) {
  return connect(null, mapDispatchToProps)(
    function WithChangeMenu(props) {
      return (<ComponentClass {...props}/>)
    })
}

export default withChangeMenu
