import React from 'react'
import { connect } from 'react-redux'


function mapStateToProps(state) {
  return {
    storedOrders: state.storedOrders
  }
}

function mapDispatchToProps(dispatch) {
  return {
    onStoredOrders: (payload) => {
      dispatch({
        type: 'FETCH_STORED_ORDERS',
        payload: payload
      })
    }
  }
}

function withStoredOrders(ComponentClass) {
  return connect(mapStateToProps, mapDispatchToProps)(
    function WithStoredOrders(props) {
      return (<ComponentClass onStoredOrders={props.onStoredOrders} {...props}/>)
    })
}

export default withStoredOrders
