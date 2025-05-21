import React from 'react'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'
import { FlexChild, FlexGrid } from '3s-widgets'

import { IconStyle } from '../../../../constants/commonStyles'
import ActionButton from '../../../../component/action-button'
import withState from '../../../../util/withState'
import { NumPad } from '../../../../component/dialogs/numpad-dialog'


function LoginNumpadRenderer({ showNumpad, showButton, blockMessage, onLogin, userId, onUserIdChange, classes }) {
  function renderNumPad() {
    if (showNumpad) {
      return (
        <NumPad
          value={userId}
          onTextChange={onUserIdChange}
          forceFocus={true}
          showDoubleZero={true}
          currencyMode={false}
          textAlign="right"
          onEnterPressed={onLogin}
        />
      )
    } else if (blockMessage != null) {
      return (
        <div className={classes.blockMessageContainer}>
          {blockMessage}
        </div>
      )
    }
    return null
  }

  function renderButton() {
    if (showButton) {
      return (
        <ActionButton
          defaultText="Login"
          onClick={onLogin}
          inlineText={true}
          disabled={showNumpad && userId === ''}
          className={showNumpad ? 'test_LoginNumpad_SIGNIN' : 'test_LoginNumpad_SIGNOUT'}
        >
          <IconStyle
            className={`${showNumpad ? 'fa-sign-in-alt' : 'fa-sign-out-alt'} fas fa-2x`}
            aria-hidden="true"
            disabled={showNumpad && userId === ''}
            secondaryColor
          />
          <I18N id={showNumpad ? '$LOGIN' : '$CLOSE_USER'}/>
        </ActionButton>
      )
    }
    return null
  }

  if (showNumpad || showButton) {
    return (
      <div className={classes.loginNumPadContainer}>
        <FlexGrid direction={'column'}>
          <FlexChild size={7}>
            {renderNumPad()}
          </FlexChild>
          <FlexChild size={1}>
            {renderButton()}
          </FlexChild>
        </FlexGrid>
      </div>
    )
  }
  return (
    <div className={classes.blockMessageContainer}>
      {blockMessage}
    </div>
  )
}

LoginNumpadRenderer.propTypes = {
  showNumpad: PropTypes.bool,
  showButton: PropTypes.bool,
  blockMessage: PropTypes.object,
  onLogin: PropTypes.func,
  userId: PropTypes.string,
  onUserIdChange: PropTypes.func,
  classes: PropTypes.object,
  workingMode: PropTypes.object
}

export default withState(LoginNumpadRenderer, 'workingMode')
