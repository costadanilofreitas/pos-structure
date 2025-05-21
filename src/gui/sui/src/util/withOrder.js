import React from 'react'
import { connect } from 'react-redux'

function mapStateToProps(state) {
  return {
    order: state.order
  }
}

function withOrder(ComponentClass) {
  return connect(mapStateToProps)(
    function WithOrder(props) {
      return (<ComponentClass order={props.order} {...props}/>)
    })
}

export default withOrder
