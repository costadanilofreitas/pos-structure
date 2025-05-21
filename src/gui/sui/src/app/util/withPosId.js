import React from 'react'
import { connect } from 'react-redux'


function mapStateToProps(state) {
  return {
    posId: state.posId
  }
}

function withPosId(ComponentClass) {
  return connect(mapStateToProps)(
    function WithPosId(props) {
      return (<ComponentClass posId={props.posId} {...props}/>)
    })
}

export default withPosId
