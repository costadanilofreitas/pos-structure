import React from 'react'
import { connect } from 'react-redux'

function mapStateToProps(state) {
  return {
    dialogs: state.dialogs
  }
}

function withDialogs(ComponentClass) {
  return connect(mapStateToProps)(
    function WithDialogs(props) {
      return (<ComponentClass order={props.dialogs} {...props}/>)
    })
}

export default withDialogs
