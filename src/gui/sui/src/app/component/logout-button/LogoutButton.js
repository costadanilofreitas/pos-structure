import React, { Component } from 'react'

import { I18N } from '3s-posui/core'
import PropTypes from 'prop-types'

import { IconStyle, CommonStyledButton } from '../../../constants/commonStyles'
import withExecuteActionMessageBus from '../../../util/withExecuteActionMessageBus'
import MessageBusPropTypes from '../../../prop-types/MessageBusPropTypes'
import withChangeMenu from '../../util/withChangeMenu'


class LogoutButton extends Component {
  constructor(props) {
    super(props)

    this.handleOnLogout = this.handleOnLogout.bind(this)
  }

  render() {
    return (
      <CommonStyledButton
        border={true}
        onClick={this.handleOnLogout}
      >
        <IconStyle className="fas fa-sign-out-alt fa-2x" aria-hidden="true"/><br/>
        <I18N id="$LOGOUT"/>
      </CommonStyledButton>
    )
  }

  handleOnLogout() {
    this.props.msgBus.syncAction('pause_user').then(response => {
      if (response.ok && response.data === 'True') {
        this.props.changeMenu(null)
      }
    })
  }
}

LogoutButton.propTypes = {
  msgBus: MessageBusPropTypes,
  changeMenu: PropTypes.func
}

export default withChangeMenu(withExecuteActionMessageBus(LogoutButton))
