import React from 'react'
import { connect } from 'react-redux'
import { ABANDON_POS } from '../../constants/actionTypes'


function mapDispatchToProps(dispatch) {
  return {
    abandonPos: function () {
      dispatch({ type: ABANDON_POS, payload: null })
    }
  }
}

function withAbandonPos(ComponentClass) {
  return connect(null, mapDispatchToProps)(
    function WithAbandonPos(props) {
      return (<ComponentClass {...props}/>)
    })
}

export default withAbandonPos
