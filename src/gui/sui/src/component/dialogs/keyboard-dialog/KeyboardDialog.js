import React, { Component } from 'react'
import PropTypes from 'prop-types'
import KeyboardDialogRenderer from './keyboard-dialog'


class KeyboardDialog extends Component {
  render() {
    return <KeyboardDialogRenderer{...this.props}/>
  }
}

KeyboardDialog.propTypes = {
  flatStyle: PropTypes.bool,
  type: PropTypes.string,
  message: PropTypes.string,
  closeDialog: PropTypes.func,
  title: PropTypes.string,
  mask: PropTypes.string,
  default: PropTypes.string,
  onDialogClose: PropTypes.func,
  nopad: PropTypes.bool
}

KeyboardDialog.defaultProps = {
  flatStyle: true,
  nopad: false
}

export default (KeyboardDialog)
