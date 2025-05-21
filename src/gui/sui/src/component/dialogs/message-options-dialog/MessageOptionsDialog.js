import React, { Component } from 'react'
import PropTypes from 'prop-types'
import MessageOptionsDialogRenderer from './message-options-dialog-renderer'
import withState from '../../../util/withState'


class MessageOptionsDialog extends Component {
  render() {
    return <MessageOptionsDialogRenderer{...this.props}/>
  }
}

MessageOptionsDialog.propTypes = {
  flatStyle: PropTypes.bool,
  type: PropTypes.string,
  message: PropTypes.oneOfType([PropTypes.string, PropTypes.array]),
  closeDialog: PropTypes.func,
  title: PropTypes.string,
  mask: PropTypes.string,
  default: PropTypes.string,
  onDialogClose: PropTypes.func,
  screenOrientation: PropTypes.number
}

MessageOptionsDialog.defaultProps = {
  flatStyle: true
}

export default withState(MessageOptionsDialog, 'screenOrientation')
