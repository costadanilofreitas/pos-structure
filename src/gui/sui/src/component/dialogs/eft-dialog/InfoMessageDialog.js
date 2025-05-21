import React, { Component } from 'react'
import PropTypes from 'prop-types'
import InfoMessageDialogRenderer from './renderer'


class InfoMessageDialog extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    const { infoMessage, flatStyle } = this.props

    if (infoMessage != null) {
      if (infoMessage.msg != null) {
        if (infoMessage.msg.includes('#SHOW|')) {
          const msg = infoMessage.msg.substring(6)
          if (msg !== '') {
            return <InfoMessageDialogRenderer flatStyle={flatStyle} message={msg}/>
          }
        }
      }
    }

    return null
  }
}

InfoMessageDialog.propTypes = {
  infoMessage: PropTypes.object,
  flatStyle: PropTypes.bool
}

export default InfoMessageDialog
