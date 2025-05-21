import React from 'react'
import { connect } from 'react-redux'


function mapStateToProps({ locale, timeDelta }) {
  return {
    messages: locale.messages || {},
    timeDelta: timeDelta
  }
}

function withGetCurrentDate(ComponentClass) {
  return connect(mapStateToProps)(
    function WithGetMessages(props) {
      return (<ComponentClass getCurrentDate={() => {
        return new Date(new Date().getTime() + props.timeDelta)
      }} {...props}/>)
    })
}

export default withGetCurrentDate
