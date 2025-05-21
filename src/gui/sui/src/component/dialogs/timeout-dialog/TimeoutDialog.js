import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'

import injectSheet, { jss } from 'react-jss'
import withCloseDialog from '../../../app/util/withCloseDialog'
import MessageOptionsDialog from '../message-options-dialog'


jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = {
  clickArea: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    top: 0,
    zIndex: 1000
  },
  messageClassName: {
    fontSize: '30vmin'
  }
}

class TimeoutDialog extends PureComponent {
  handleCloseDialog = () => {
    this.props.closeDialog('timeout_id')
  }

  render() {
    const { classes, message, flatStyle } = this.props
    const messageClass = classes.messageClassName

    return (
      <div className={`${classes.clickArea} test_TimeoutDialog_TIMEOUT`} onClick={this.handleCloseDialog}>
        <MessageOptionsDialog title={'$TIMEOUT'} flatStyle={flatStyle} message={message} messageClassName={messageClass} btn={[]}/>
      </div>
    )
  }
}

TimeoutDialog.propTypes = {
  classes: PropTypes.object,
  message: PropTypes.string,
  closeDialog: PropTypes.func,
  flatStyle: PropTypes.bool
}

export default withCloseDialog(injectSheet(styles)(TimeoutDialog))
