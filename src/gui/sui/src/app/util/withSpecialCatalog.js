import React from 'react'
import { connect } from 'react-redux'

function mapStateToProps(state) {
  return {
    specialCatalog: state.specialCatalog
  }
}

function withSpecialCatalog(ComponentClass) {
  return connect(mapStateToProps)(
    function WithSpecialCatalog(props) {
      return (<ComponentClass posId={props.specialCatalog} {...props}/>)
    })
}

export default withSpecialCatalog
