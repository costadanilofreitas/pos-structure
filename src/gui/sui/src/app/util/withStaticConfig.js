import React from 'react'
import { connect } from 'react-redux'


function mapStateToProps(state) {
  return {
    staticConfig: state.staticConfig
  }
}

function withStaticConfig(ComponentClass) {
  return connect(mapStateToProps)(
    function WithStaticConfig(props) {
      return (<ComponentClass {...props}/>)
    })
}

export default withStaticConfig
