import React from 'react'
import { connect } from 'react-redux'

function mapStateToProps(state) {
  return {
    showTabs: state.showTabs
  }
}

function withShowTabs(ComponentClass) {
  return connect(mapStateToProps)(
    function WithShowTabs(props) {
      return (<ComponentClass showTabs={props.showTabs} {...props}/>)
    })
}

export default withShowTabs
