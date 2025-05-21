import React, { Component } from 'react'
import { FlexChild, FlexGrid, ScrollPanel } from '3s-widgets'
import { I18N } from '3s-posui/core'
import PropTypes from 'prop-types'
import KeyboardWrapper from './KeyboardWrapper'
import { isEnter, isEsc } from '../../../../util/keyboardHelper'
import withState from '../../../../util/withState'
import ScreenOrientation from '../../../../constants/ScreenOrientation'
import { IconStyle, PopupStyledButton } from '../../../../constants/commonStyles'
import {
  ButtonsContainer,
  CenterInput,
  CommentLine,
  Comments,
  MessageBackground,
  Messages,
  MessageTitleContainer,
  MessageTitle
} from './StyledKeyboardDialog'

class KeyboardDialogRenderer extends Component {
  constructor(props) {
    super(props)

    this.state = {
      value: this.props.default || '',
      visible: true,
      selectedComment: -1
    }

    this.handleOnOk = this.handleOnOk.bind(this)
    this.handleOnCancel = this.handleOnCancel.bind(this)
    this.handleKeyPressed = this.handleKeyPressed.bind(this)
    this.handleOnInputChange = this.handleOnInputChange.bind(this)
    this.handleOnSelectComment = this.handleOnSelectComment.bind(this)
  }

  messagesMinHeightValue() {
    const { mobile, screenOrientation } = this.props
    if (mobile) {
      return 'calc(100% / 12 * 3)'
    }
    if (screenOrientation === ScreenOrientation.Portrait) {
      return 'calc(100% / 12 * 5)'
    }
    return 'calc(100% / 12 * 7)'
  }

  centerInputFlex() {
    const { mobile, screenOrientation } = this.props
    if (mobile) {
      return 1
    }
    if (screenOrientation === ScreenOrientation.Portrait) {
      return 3
    }
    return 5
  }

  render() {
    const { mask, info, mobile, flatStyle, screenOrientation, message, nopad } = this.props
    const { visible, value, selectedComment } = this.state

    if (!visible) {
      return null
    }

    const comments = (mobile || info == null || info === '' || info === '$PRESS_OK_TO_CONTINUE')
      ? []
      : [' '].concat(info.split('|'))
    const hideCancelButton = mask.toString().toLocaleLowerCase() !== 'no_cancel'

    return (
      <MessageBackground flat={flatStyle}>
        <Messages
          minHeight={this.messagesMinHeightValue()}
          vertical={screenOrientation === ScreenOrientation.Portrait}
          hideKeys={mobile}
          flat={flatStyle}
        >
          <div className={'absoluteWrapper'}>
            <FlexGrid direction={'column'}>
              <FlexChild size={1}>
                <MessageTitleContainer flat={flatStyle}>
                  <MessageTitle flat={flatStyle}>
                    <I18N id={message}/>
                  </MessageTitle>
                </MessageTitleContainer>
              </FlexChild>
              <FlexChild size={this.centerInputFlex()}>
                <CenterInput flat={flatStyle}>
                  <FlexGrid direction={'row'}>
                    {comments.length > 0 &&
                    <FlexChild size={1}>
                      <Comments flat={flatStyle}>
                        <ScrollPanel>
                          {comments.map((comment, index) => {
                            return (
                              <CommentLine
                                flat={flatStyle}
                                selected={index === selectedComment && comment === value}
                                key={index}
                                onClick={() => this.handleOnSelectComment(index, comment)}
                              >
                                {comment}
                              </CommentLine>
                            )
                          })}
                        </ScrollPanel>
                      </Comments>
                    </FlexChild>
                    }
                    <FlexChild size={2}>
                      <CenterInput flat={flatStyle}>
                        <KeyboardWrapper
                          flatStyle={flatStyle}
                          value={value}
                          handleOnOk={this.handleOnOk}
                          handleOnCancel={this.handleOnCancel}
                          handleOnInputChange={this.handleOnInputChange}
                          keyboardVisible={true}
                          showHideKeyboardButton={false}
                          flat={flatStyle}
                          nopad={nopad}
                        />
                      </CenterInput>
                    </FlexChild>
                  </FlexGrid>
                </CenterInput>
              </FlexChild>
              <FlexChild size={1}>
                <FlexGrid>
                  {hideCancelButton &&
                  <ButtonsContainer flat={flatStyle}>
                    <PopupStyledButton
                      active={true}
                      flexButton={true}
                      borderRight={true}
                      flat={flatStyle}
                      className={' test_KeyboardDialog_CANCEL'}
                      onClick={this.handleOnCancel}
                    >
                      <div>
                        <IconStyle overrideColor="#FFF" className="fa fa-ban fa-2x" aria-hidden="true" totem={!flatStyle}/>
                      </div>
                      <I18N id="$CANCEL"/>
                    </PopupStyledButton>
                  </ButtonsContainer>
                  }
                  <ButtonsContainer flat={flatStyle}>
                    <PopupStyledButton
                      flexButton={true}
                      active={true}
                      flat={flatStyle}
                      className={' test_KeyboardDialog_OK'}
                      onClick={this.handleOnOk}
                    >
                      <div>
                        <IconStyle overrideColor="#FFF" className="fa fa-check fa-2x" aria-hidden="true" totem={!flatStyle}/>
                      </div>
                      <I18N id="$OK"/>
                    </PopupStyledButton>
                  </ButtonsContainer>
                </FlexGrid>
              </FlexChild>
            </FlexGrid>
          </div>
        </Messages>
      </MessageBackground>
    )
  }

  componentDidMount() {
    document.addEventListener('keydown', this.handleKeyPressed, false)
  }

  componentWillUnmount() {
    document.removeEventListener('keydown', this.handleKeyPressed, false)
  }

  handleKeyPressed(event) {
    if (isEnter(event)) {
      this.handleOnOk()
    }
    if (isEsc(event)) {
      this.handleOnCancel()
    }
  }

  handleOnOk() {
    this.props.closeDialog(0, this.state.value)
  }

  handleOnCancel() {
    this.props.closeDialog('-1')
  }

  handleOnInputChange(value) {
    this.setState({ value: value })
  }

  handleOnSelectComment(selectedComment, comment) {
    this.setState({ selectedComment: selectedComment, value: comment })
  }
}

KeyboardDialogRenderer.propTypes = {
  flatStyle: PropTypes.bool,
  closeDialog: PropTypes.func,
  message: PropTypes.string,
  default: PropTypes.string,
  mobile: PropTypes.bool,
  mask: PropTypes.string,
  info: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
  nopad: PropTypes.bool,
  screenOrientation: PropTypes.number
}

export default (withState(KeyboardDialogRenderer, 'mobile', 'screenOrientation'))
