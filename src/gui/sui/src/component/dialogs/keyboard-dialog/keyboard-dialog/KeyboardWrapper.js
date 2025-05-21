import React, { Component } from 'react'
import injectSheet from 'react-jss'
import PropTypes from 'prop-types'

import { Keyboard, LatinLayout } from '3s-posui/keyboard'
import { FlexChild, FlexGrid } from '3s-widgets'

import KeyboardInput from './KeyboardInput'
import withState from '../../../../util/withState'
import { Input, KeyboardHideShow } from './StyledKeyboardDialog'
import { includesMask } from '../../../../util/keyboardHelper'


const styles = (theme) => ({
  keyboardButtons: {
    width: '100%',
    backgroundColor: theme.keyboardButton
  },
  keyboardButtonsPressed: {
    backgroundColor: theme.keyboardButtonPressed
  }
})

class KeyboardWrapper extends Component {
  constructor(props) {
    super(props)

    this.handleInputChange = this.handleInputChange.bind(this)
    this.handleKeyPressed = this.handleKeyPressed.bind(this)
    this.handleKeyPressedKeyboard = this.handleKeyPressedKeyboard.bind(this)
  }

  render() {
    if (!this.props.visible) {
      return null
    }

    return (this.props.mobile === false ? this.renderDesktopKeyboard() : this.renderMobileKeyboard())
  }

  renderDesktopKeyboard() {
    const {
      classes, value, handleShowHideKeyboardButton, keyboardVisible, showHideKeyboardButton, readOnly, flat,
      leftButtons, rightButtons, keyboardFlexSize, autoFocus, showInput, mask, onBlur, showBackspace
    } = this.props

    return (
      <FlexGrid direction={'column'}>
        {showInput &&
        <FlexChild size={1}>
          <FlexGrid direction={'row'}>
            <FlexChild size={9}>
              { showInput &&
                <KeyboardInput
                  mask={mask}
                  flatStyle={this.props.flatStyle}
                  value={value}
                  classes={classes}
                  readOnly={readOnly === true}
                  onSetKeyPressedHandler={this.handleKeyPressedKeyboard}
                  onInputChange={this.handleChangeKeyboard}
                  onInputKeyUp={this.handleKeyPressedKeyboard}
                  flat={flat}
                  autoFocus={autoFocus}
                  onBlur={onBlur}
                />
              }
            </FlexChild>
            {showHideKeyboardButton &&
            <FlexChild size={1}>
              <KeyboardHideShow
                onClick={handleShowHideKeyboardButton}
                className={'test_KeyboardWrapper_KEYBOARD-SHOW'}
              >
                <i
                  className={keyboardVisible ? 'fa fa-chevron-up fa-2x' : 'fa fa-keyboard fa-2x'}
                  aria-hidden="true"
                  style={{ margin: '0.5vmin' }}
                />
              </KeyboardHideShow>
            </FlexChild>
            }
          </FlexGrid>
        </FlexChild>
        }
        { keyboardVisible &&
        <FlexChild size={keyboardFlexSize != null ? keyboardFlexSize : 4}>
          <Keyboard
            value={value}
            layouts={[LatinLayout]}
            leftButtons={leftButtons}
            rightButtons={rightButtons}
            buttonClassNamePressed={classes.keyboardButtonsPressed}
            startWithCaps={false}
            onChange={this.handleChange}
            onKeyPressed={this.handleKeyPressed}
            buttonClassName={classes.keyboardButtons}
            showAt={false}
            showNumbers={!this.props.nopad}
            showBackspace={showBackspace}
          />
        </FlexChild>
        }
      </FlexGrid>
    )
  }

  renderMobileKeyboard() {
    const { value, flat, autoFocus } = this.props

    return (
      <FlexChild size={2}>
        <Input>
          <KeyboardInput
            flatStyle={this.props.flatStyle}
            value={value}
            onInputChange={this.handleInputChange}
            flat={flat}
            autoFocus={autoFocus}
          />
        </Input>
      </FlexChild>
    )
  }

  handleChange = (event) => {
    this.props.handleOnInputChange(event.target.value)
  }

  handleChangeKeyboard = (value) => {
    this.props.handleOnInputChange(value)
  }

  handleInputChange = (value) => {
    this.props.handleOnInputChange(value)
  }

  isValidValue(mask, value, input) {
    const canBeNumber = mask[value.length - 1] === '9' && !isNaN(input)
    const canBeString = mask[value.length - 1] === 'a' && (typeof input) === 'string'
    const canBeAnything = mask[value.length - 1] === '*'
    const fitsInMask = mask.length >= value.length
    const isBackspace = input === 'backspace'
    return (canBeNumber || canBeString || canBeAnything || isBackspace) && fitsInMask
  }

  updateValueMask(mask, value) {
    let newValue = value
    const startPoint = newValue.length
    const nonMaskedValues = mask.replace(/[9a*]/g, '')
    if (nonMaskedValues) {
      for (let i = 0; i < mask.length; i++) {
        const nextMask = mask[startPoint + i]
        if (nextMask && !includesMask(nextMask)) {
          newValue += mask[startPoint + i]
        } else {
          break
        }
      }
    }
    return newValue
  }

  maskChanged(value, mask) {
    const newValue = value.replace(/[a-z0-9]/g, '')
    const newMask = mask.substring(0, value.length).replace(/[a-z0-9]/g, '')
    return newValue !== newMask
  }

  handleKeyPressed(event) {
    const { mask } = this.props

    if (event.keyCode === 8) {
      return
    }

    if (event.keyCode === 13 && this.props.handleOnOk != null) {
      this.props.handleOnOk()
    } else if (event.keyCode === 27 && this.props.handleOnCancel != null) {
      this.props.handleOnCancel()
    } else if (event.keyCode === 8) {
      const value = this.state.value.substr(0, this.state.value.length - 1)
      this.setState({ value })
      this.props.handleOnInputChange(value)
    } else {
      let value = ''
      if (event === 'backspace') {
        value = this.props.value.toLowerCase()
        if (mask) {
          value = value.replace(/[^0-9a-z]/g, '')
        }
        value = value.substr(0, value.length - 1)
      } else {
        if (typeof (event) === 'string' || typeof (event) === 'number') {
          value = event
        } else if (event.keyCode >= 48 && event.keyCode <= 57) {
          value = (event.keyCode - 48).toString()
        } else if (event.keyCode >= 96 && event.keyCode <= 105) {
          value = (event.keyCode - 96).toString()
        }
        value = this.props.value + value
      }
      if (mask) {
        if (this.maskChanged(value, mask)) {
          const regexValue = value.replace(/[^a-z0-9]/g, '')
          let newValue = ''
          let regexIndex = 0
          for (let i = 0; i < mask.length; i++) {
            if (!includesMask(mask[i])) {
              newValue += mask[i]
            } else if (regexValue[regexIndex]) {
              newValue += regexValue[regexIndex]
              regexIndex += 1
            } else {
              break
            }
          }
          value = newValue
        }
        if (!this.isValidValue(mask, value, event)) {
          return
        }
        if (!includesMask(mask[value.length])) {
          value = this.updateValueMask(mask, value)
        }
      }
      this.props.handleOnInputChange(value)
    }
  }

  handleKeyPressedKeyboard(event) {
    if (event.keyCode === 13 && this.props.handleOnOk != null) {
      this.props.handleOnOk()
    } else if (event.keyCode === 27 && this.props.handleOnCancel != null) {
      this.props.handleOnCancel()
    }
  }
}

KeyboardWrapper.propTypes = {
  classes: PropTypes.object,
  mobile: PropTypes.bool,
  value: PropTypes.string,
  readOnly: PropTypes.bool,
  visible: PropTypes.bool,
  keyboardVisible: PropTypes.bool,
  showHideKeyboardButton: PropTypes.bool,
  handleOnOk: PropTypes.func,
  handleOnCancel: PropTypes.func,
  handleOnInputChange: PropTypes.func,
  handleShowHideKeyboardButton: PropTypes.func,
  flatStyle: PropTypes.bool,
  flat: PropTypes.bool,
  nopad: PropTypes.bool,
  leftButtons: PropTypes.array,
  rightButtons: PropTypes.array,
  keyboardFlexSize: PropTypes.number,
  autoFocus: PropTypes.bool,
  showInput: PropTypes.bool,
  mask: PropTypes.string,
  onBlur: PropTypes.func,
  showBackspace: PropTypes.bool
}


KeyboardWrapper.defaultProps = {
  visible: true,
  leftButtons: [],
  rightButtons: [],
  showInput: true,
  mask: null,
  onBlur: null,
  showBackspace: false
}

export default injectSheet(styles)(withState(KeyboardWrapper, 'mobile'))
