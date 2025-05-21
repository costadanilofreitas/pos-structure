import React, { Component } from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'
import { FlexChild, FlexGrid, ScrollPanel } from '3s-widgets'

import { I18N } from '3s-posui/core'
import { getMessageKey } from '../../../../util/i18nUtil'
import { isEnter, isEsc, isTab } from '../../../../util/keyboardHelper'
import {
  ButtonsContainer,
  MainMessageContainer,
  MessageBackground,
  MessageButton,
  MessageTitleContainer,
  MessageTitle,
  Message,
  MessageContainer
} from './StyledMessageOptionsDialog'
import { IconStyle } from '../../../../constants/commonStyles'
import withState from '../../../../util/withState'

function renderIcon(button, flatStyle = true) {
  let icon
  switch (button) {
    case '$TABS': {
      icon = <IconStyle className={'fas fa-pager fa-2x'} dialog={true}/>
      break
    }
    case '$TABLES': {
      icon = <IconStyle className={'fas fa-utensils fa-2x'} dialog={true}/>
      break
    }
    case '$CANCEL': {
      icon = <IconStyle className={'fas fa-ban fa-2x'} totem={!flatStyle} dialog={true}/>
      break
    }
    case '$YES': {
      icon = <IconStyle className={'fas fa-check fa-2x'} totem={!flatStyle} dialog={true}/>
      break
    }
    case '$OK': {
      icon = <IconStyle className={'fas fa-check fa-2x'} totem={!flatStyle} dialog={true}/>
      break
    }
    case '$NO': {
      icon = <IconStyle className={'fas fa-ban fa-2x'} totem={!flatStyle} dialog={true}/>
      break
    }
    case '$GO_TO_LINKED_TABLE': {
      icon = <IconStyle className={'fas fa-share fa-2x'} dialog={true}/>
      break
    }
    case '$PRINT': {
      icon = <IconStyle className={'fas fa-print fa-2x'} dialog={true}/>
      break
    }
    case '$CLOSE': {
      icon = <IconStyle className={'fas fa-times fa-2x'} dialog={true}/>
      break
    }
    case '$DESELECT_TABLE': {
      icon = <IconStyle className={'fa-2x fas fa-arrow-circle-left fa-2x'} dialog={true}/>
      break
    }
    case '$REOPEN_TABLE': {
      icon = <IconStyle className={'fa-2x fas fa-undo fa-2x'} dialog={true}/>
      break
    }
    case '$CREATE_TAB': {
      icon = <IconStyle className={'fa-2x fas fa-pager fa-2x'} dialog={true}/>
      break
    }
    case '$BACK_FROM_SOURCE_TABLE': {
      icon = <IconStyle className={'fas fa-reply fa-2x'} dialog={true}/>
      break
    }
    case '$GET_WEIGHT_AGAIN': {
      icon = <IconStyle className={'fas fa-weight fa-2x'} dialog={true}/>
      break
    }
    case '$START_DELIVERY': {
      icon = <IconStyle className={'fas fa-lock-open fa-2x'} dialog={true}/>
      break
    }
    case '$STOP_DELIVERY': {
      icon = <IconStyle className={'fas fa-lock fa-2x'} dialog={true}/>
      break
    }
    default: {
      icon = ''
    }
  }

  return icon
}

class MessageOptionsDialogRenderer extends Component {
  constructor(props) {
    super(props)

    this.state = {
      visible: true,
      focusedIndex: 0
    }

    this.handleOnConfirm = this.handleOnConfirm.bind(this)
    this.handleKeyPressed = this.handleKeyPressed.bind(this)
  }

  messageWidth() {
    const { isPrintPreview, screenOrientation, mobile } = this.props
    if (mobile) {
      return '100%'
    } else if (isPrintPreview) {
      if (screenOrientation === ScreenOrientation.Portrait) {
        return '85%'
      }
      return '40%'
    }
    return '70%'
  }

  messageHeight() {
    const { isPrintPreview, screenOrientation } = this.props

    if (isPrintPreview) {
      return 'calc(100% / 12 * 11)'
    } else if (screenOrientation === ScreenOrientation.Portrait) {
      return 'calc(100% / 12 * 4)'
    }
    return 'calc(100% / 12 * 7)'
  }

  messageBottom() {
    const { flatStyle, screenOrientation } = this.props

    if (flatStyle) {
      return '0'
    } else if (screenOrientation === ScreenOrientation.Portrait) {
      return '-1vmin'
    }
    return '0.3vmin'
  }

  flexSize() {
    const { screenOrientation } = this.props
    if (screenOrientation === ScreenOrientation.Portrait) {
      return 2
    }
    return 5
  }

  render() {
    const { title, isPrintPreview } = this.props
    const { visible } = this.state

    if (!visible) {
      return null
    }

    const messageRenderer =
      isPrintPreview
        ?
        <>
          {this.renderMainMessage()}
          <ButtonsContainer flat={this.props.flatStyle}>
            {this.renderButtons()}
          </ButtonsContainer>
        </>
        :
        (
          <>
            <FlexChild size={this.flexSize()}>
              <MainMessageContainer flat={this.props.flatStyle}>
                {this.renderMainMessage()}
              </MainMessageContainer>
            </FlexChild>
            <FlexChild>
              <ButtonsContainer flat={this.props.flatStyle}>
                {this.renderButtons()}
              </ButtonsContainer>
            </FlexChild>
          </>
        )

    return (
      <MessageBackground flat={this.props.flatStyle}>
        <Message flat={this.props.flatStyle} messageHeight={this.messageHeight()} messageWidth={this.messageWidth()}>
          <FlexGrid direction={'column'}>
            <FlexChild flat={this.props.flatStyle}>
              <MessageTitleContainer>
                <MessageTitle flat={this.props.flatStyle}>
                  <I18N id={title}/>
                </MessageTitle>
              </MessageTitleContainer>
            </FlexChild>
            {messageRenderer}
          </FlexGrid>
        </Message>
      </MessageBackground>
    )
  }

  renderMainMessage() {
    const { isPrintPreview, messageClassName, message, btn, scrollY } = this.props

    function renderPrinterPreview() {
      return (
        <ScrollPanel
          style={{ alignItems: 'center' }}
          styleCont={scrollY === true ? { overflowY: 'auto', width: 'auto' } : { width: 'auto' }}
        >
          {message.map(function (item) {
            return item
          })}
        </ScrollPanel>)
    }

    function renderTextMessage() {
      const messageClass = messageClassName == null ? '' : ` ${messageClassName}`
      return (
        <p className={`${getMessageKey(message) + messageClass} test_MessageOptionsDialog_MESSAGE`}>
          <I18N id={message}/>
        </p>
      )
    }

    let flexSize = isPrintPreview ? 9 : 5
    flexSize = btn.length === 0 ? flexSize + 1 : flexSize

    const messageRenderer =
      isPrintPreview
        ?
        renderPrinterPreview()
        :
        (
          <MessageContainer>
            {renderTextMessage()}
          </MessageContainer>
        )

    return (
      <FlexChild size={flexSize}>
        {messageRenderer}
      </FlexChild>
    )
  }

  renderButtons() {
    const { btn } = this.props

    if (btn.length === 1 && btn[0] === '') {
      return null
    }

    return (
      _.cloneDeep(btn).reverse().map((button, index) => {
        return (
          <MessageButton
            messageBottom={this.messageBottom()}
            flat={this.props.flatStyle}
            className={`test_MessageOptionsDialog_${getMessageKey(button)}`}
            onClick={() => this.handleOnConfirm(btn.length - 1 - index)}
            key={index}
          >
            {renderIcon(button, this.props.flatStyle)}
            <I18N id={button}/>
          </MessageButton>
        )
      })
    )
  }

  componentDidMount() {
    document.addEventListener('keydown', this.handleKeyPressed, false)
  }

  componentWillUnmount() {
    document.removeEventListener('keydown', this.handleKeyPressed, false)
  }

  handleOnConfirm(selectedOption) {
    this.props.closeDialog(selectedOption)
  }

  handleKeyPressed(event) {
    if (isEsc(event)) {
      this.handleOnConfirm(this.props.btn.length - 1)
    } else if (isEnter(event)) {
      this.handleOnConfirm(this.state.focusedIndex)
    } else if (isTab(event)) {
      let focusedIndex = this.state.focusedIndex - 1
      if (focusedIndex === -1) {
        focusedIndex = this.props.btn.length - 1
      }
      this.setState({ focusedIndex })
    }
  }
}

MessageOptionsDialogRenderer.defaultProps = {
  scrollY: false
}

MessageOptionsDialogRenderer.propTypes = {
  flatStyle: PropTypes.bool,
  closeDialog: PropTypes.func,
  title: PropTypes.string,
  message: PropTypes.oneOfType([PropTypes.string, PropTypes.array]),
  messageClassName: PropTypes.string,
  btn: PropTypes.array,
  isPrintPreview: PropTypes.bool,
  scrollY: PropTypes.bool,
  mobile: PropTypes.bool,
  screenOrientation: PropTypes.number
}

export default (withState(MessageOptionsDialogRenderer, 'mobile'))
