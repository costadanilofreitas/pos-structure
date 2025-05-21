import React from 'react'
import { connect } from 'react-redux'


function mapStateToProps(state) {
  return {
    tables: state.tableLists
  }
}

function withTables(ComponentClass) {
  return connect(mapStateToProps)(
    function WithTables(props) {
      return (<ComponentClass {...props}/>)
    })
}

export default withTables
