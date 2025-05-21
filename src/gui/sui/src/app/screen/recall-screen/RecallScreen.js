import React, { Component } from 'react'
import RecallScreenRenderer from './renderer'
import PropTypes from 'prop-types'

class RecallScreen extends Component{
  constructor(props) {
    super(props)
  }
  render() {
    return <RecallScreenRenderer {...this.props}/>
  }

}


RecallScreen.propTypes = {
  newMessagesCount: PropTypes.number,
  resetMessageCount: PropTypes.func
}

export default RecallScreen
