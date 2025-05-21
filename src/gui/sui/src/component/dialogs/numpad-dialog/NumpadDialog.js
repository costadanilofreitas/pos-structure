import React, { Component } from 'react'
import PropTypes from 'prop-types'
import NumpadDialogRenderer from './numpad-dialog-renderer'
import withState from '../../../util/withState'

class NumpadDialog extends Component {
  render() {
    return <NumpadDialogRenderer{...this.props}/>
  }
}

NumpadDialog.propTypes = {
  flatStyle: PropTypes.bool,
  type: PropTypes.string,
  message: PropTypes.string,
  closeDialog: PropTypes.func,
  title: PropTypes.string,
  mask: PropTypes.string,
  default: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onDialogClose: PropTypes.func,
  screenOrientation: PropTypes.number,
  blockEmptyValue: PropTypes.bool
}
NumpadDialog.defaultProps = {
  flatStyle: true,
  blockEmptyValue: false
}
export default withState(NumpadDialog, 'screenOrientation')
