import React from 'react'
import { connect } from 'react-redux'

function mapStateToProps(state) {
  return {
    showTableInfo: state.showTableInfo,
    selectedTable: state.selectedTable
  }
}

function withShowTableInfo(ComponentClass) {
  return connect(mapStateToProps)(
    function WithShowTableInfo(props) {
      return (<ComponentClass showTableInfo={props.showTableInfo} selectedTable={props.selectedTable} {...props}/>)
    })
}

export default withShowTableInfo
