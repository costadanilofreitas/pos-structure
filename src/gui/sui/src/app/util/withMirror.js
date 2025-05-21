import React from 'react'
import { connect } from 'react-redux'

function mapStateToProps(state) {
  return {
    mirror: (state.custom || {}).MIRROR_SCREEN === 'true'
  }
}

function withMirror(ComponentClass) {
  return connect(mapStateToProps)(
    function WithPosId(props) {
      return (<ComponentClass mirror={props.mirror} {...props}/>)
    })
}

export default withMirror
