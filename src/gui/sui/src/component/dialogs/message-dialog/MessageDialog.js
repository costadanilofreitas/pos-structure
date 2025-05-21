import React, { Component } from 'react'
import PropTypes from 'prop-types'

import MessageOptionsDialog from '../message-options-dialog'


export default class MessageDialog extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    const showConfirmButton = this.props.mask !== 'NOCONFIRM'
    return <MessageOptionsDialog {...this.props} btn={showConfirmButton ? ['$OK'] : []}/>
  }
}

MessageDialog.propTypes = {
  classes: PropTypes.object,
  closeDialog: PropTypes.func,
  title: PropTypes.string,
  message: PropTypes.string,
  mask: PropTypes.string
}
