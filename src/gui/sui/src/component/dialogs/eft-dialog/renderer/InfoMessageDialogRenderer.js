import React, { Component } from 'react'
import PropTypes from 'prop-types'
import MessageOptionsDialog from '../../message-options-dialog'

class InfoMessageDialogRenderer extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    const { classes, message } = this.props
    const messageClass = classes.messageClassName

    return (
      <div className={classes.clickArea}>
        <MessageOptionsDialog flatStyle={this.props.flatStyle} title={'$EFT'} message={message} messageClassName={messageClass} btn={[]}/>
      </div>
    )
  }
}

InfoMessageDialogRenderer.propTypes = {
  classes: PropTypes.object,
  flatStyle: PropTypes.bool,
  message: PropTypes.string
}

export default InfoMessageDialogRenderer
