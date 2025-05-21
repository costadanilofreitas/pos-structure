import React from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'
import { AutoFocusComponent } from '3s-posui/utils'
import injectSheet, { jss } from 'react-jss'
import InputMask from 'react-input-mask'

import {
  KeyboardInputBackspaceRoot,
  KeyboardInputCont,
  KeyboardInputRoot,
  KeyboardInputWrapper
} from './StyledKeyboardDialog'
import { includesMask } from '../../../../util/keyboardHelper'


jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = (theme) => ({
  keyboardInput: {
    textTransform: 'uppercase',
    composes: 'keyboard-input',
    width: '100%',
    outline: 'none',
    border: 'none',
    display: 'flex',
    backgroundColor: theme.inputBackground,
    fontWeight: 'bold',
    textAlign: 'left',
    fontFamily: 'sans-serif, monospace',
    '&::selection': {
      backgroundColor: 'black',
      color: 'white'
    },
    '&:placeholder-shown': {
      fontFamily: 'Arial Bold, Arial',
      fontWeight: 'normal',
      fontSize: '2.5vmin'
    }
  }
})

class KeyboardInput extends AutoFocusComponent {
  state = {
    focused: false
  }

  componentDidMount() {
    const { onSetKeyPressedHandler, autoFocus } = this.props
    const inputNode = this.input
    if (!inputNode) {
      return
    }
    const { value } = inputNode
    if (autoFocus) {
      _.defer(() => {
        const len = (value || '').length
        inputNode.setSelectionRange(len, len)
      })
    }
    if (onSetKeyPressedHandler) {
      onSetKeyPressedHandler(this.handleKeyPressed)
    }
  }

  handleBackspaceClick = () => {
    const { onInputChange, value, autoFocus, mask } = this.props
    const inputNode = this.input
    if (!inputNode) {
      return
    }
    let { selectionStart, selectionEnd } = inputNode
    let nextValue
    let nextSelectionPosition
    if (mask && value.length > 0) {
      selectionStart = value.length
      selectionEnd = value.length
    }
    if (selectionStart === selectionEnd) {
      if (mask && !includesMask(mask[selectionStart - 1])) {
        const maskSlice = mask.slice(0, selectionStart)
        const nonValueIdx = [maskSlice.lastIndexOf('9'), maskSlice.lastIndexOf('a'), maskSlice.lastIndexOf('*')]
        const maxNonValueIdx = Math.max(...nonValueIdx)
        const startDiff = selectionStart - maxNonValueIdx
        if (maxNonValueIdx < 0) {
          nextValue = value.substring(0, selectionStart) + value.substring(selectionEnd)
          nextSelectionPosition = selectionStart
        } else {
          nextValue = value.substring(0, selectionStart - startDiff) + value.substring(selectionEnd)
          nextSelectionPosition = selectionStart - startDiff
        }
      } else {
        nextValue = value.substring(0, selectionStart - 1) + value.substring(selectionEnd)
        nextSelectionPosition = selectionStart - 1
      }
    } else {
      nextValue = value.substring(0, selectionStart) + value.substring(selectionEnd)
      nextSelectionPosition = selectionStart
    }
    nextSelectionPosition = (nextSelectionPosition > 0) ? nextSelectionPosition : 0

    if (autoFocus) {
      _.defer(() => {
        inputNode.focus()
        inputNode.setSelectionRange(nextSelectionPosition, nextSelectionPosition)
      })
    }
    onInputChange(nextValue)
  }

  handleInputChange = (event) => {
    const { onInputChange } = this.props
    onInputChange(event.target.value.toUpperCase())
  }

  handleKeyPressed = (key) => {
    const inputNode = this.input
    if (!inputNode) {
      return
    }
    const { value, onInputChange, autoFocus } = this.props
    const { selectionStart, selectionEnd } = inputNode
    const nextValue = value.substring(0, selectionStart) + key + value.substring(selectionEnd)

    if (autoFocus) {
      _.defer(() => {
        inputNode.focus()
        inputNode.setSelectionRange(selectionStart + 1, selectionStart + 1)
      })
    }
    inputNode.dispatchEvent(new Event('input'))
    onInputChange(nextValue)
  }

  onBlur() {
    setState({ focused: false })
    this.props.onBlur()
  }

  render() {
    const {
      classes, onInputKeyUp, value, inputType, autoFocus, readOnly, flat, paddingBackspace, onBlur, onFocus, mask,
      maskChar, beforeMaskedValueChange, showBackspace
    } = this.props

    const keyboard = (
      <>
        <KeyboardInputWrapper>
          <InputMask
            mask={mask}
            beforeMaskedValueChange={beforeMaskedValueChange}
            maskChar={maskChar}
            inputRef={(el) => (this.input = el)}
            onChange={this.handleInputChange}
            value={value}
            onKeyUp={onInputKeyUp}
            autoFocus={autoFocus}
            style={{ fontSize: paddingBackspace ? '2vmin' : '3vmin' }}
            className={`${classes.keyboardInput} test_KeyboardInput_INPUT`}
            type={inputType}
            readOnly={readOnly}
            onBlur={onBlur}
            onFocus={onFocus}
          />
        </KeyboardInputWrapper>
        {showBackspace &&
          <KeyboardInputBackspaceRoot
            paddingBackspace={paddingBackspace}
            className={' test_KeyboardInput_DELETE'}
            onClick={this.handleBackspaceClick}
          >
            <i className={'fas fa-backspace fa-2x'} aria-hidden="true" style={{ margin: '0.5vmin', fontSize: '4vmin' }}/>
          </KeyboardInputBackspaceRoot>
        }
      </>
    )
    return (
      <KeyboardInputRoot>
        <KeyboardInputCont flat={flat}>{keyboard}</KeyboardInputCont>
      </KeyboardInputRoot>
    )
  }
}

KeyboardInput.propTypes = {
  classes: PropTypes.object,
  onInputChange: PropTypes.func,
  onInputKeyUp: PropTypes.func,
  value: PropTypes.string.isRequired,
  inputType: PropTypes.string,
  onSetKeyPressedHandler: PropTypes.func,
  autoFocus: PropTypes.bool,
  readOnly: PropTypes.bool,
  flat: PropTypes.bool,
  paddingBackspace: PropTypes.bool,
  onBlur: PropTypes.func,
  onFocus: PropTypes.func,
  mask: PropTypes.string,
  maskChar: PropTypes.string,
  beforeMaskedValueChange: PropTypes.func,
  showBackspace: PropTypes.bool
}

KeyboardInput.defaultProps = {
  onInputChange: () => null,
  onInputKeyUp: () => null,
  autoFocus: true,
  readOnly: false,
  mask: null,
  maskChar: null,
  flat: false,
  onBlur: () => null,
  onFocus: () => null,
  beforeMaskedValueChange: null,
  showBackspace: true
}

export default injectSheet(styles)(KeyboardInput)
