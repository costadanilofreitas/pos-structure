import React from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'
import injectSheet, { jss } from 'react-jss'
import { AutoFocusComponent } from '../utils'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = {
  keyboardInputRoot: {
    composes: 'keyboard-input-root',
    width: '100%',
    height: '7vh'
  },
  keyboardInputCont: {
    composes: 'keyboard-input-cont',
    display: 'flex',
    alignItems: 'center',
    backgroundColor: 'white',
    width: '100%',
    height: '100%',
    position: 'relative'
  },
  keyboardInputWrapper: {
    composes: 'keyboard-input-wrapper',
    position: 'relative',
    paddingTop: '0.7vh',
    paddingBottom: '0.7vh',
    paddingLeft: '2%',
    flexGrow: 1,
    flexShrink: 1,
    flexBasis: '0',
    boxSizing: 'border-box'
  },
  keyboardInput: {
    composes: 'keyboard-input',
    width: '100%',
    fontSize: '3vh',
    outline: 'none',
    border: 'none',
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
      fontSize: '2.5vh'
    }
  },
  keyboardInputBackspaceRoot: {
    composes: 'keyboard-input-backspace-root',
    position: 'relative',
    height: '100%',
    width: '100%',
    padding: '1vh 2%',
    flexGrow: 0,
    flexShrink: 0,
    flexBasis: '0',
    boxSizing: 'border-box'
  }
}

/**
 * Helper input component that can be used in conjunction with `Keyboard` in order
 * to implement an on-screen keyboard suitable for POS touchscreen.
 *
 * Available class names:
 * - main container element: `keyboard-input-root`
 * - input container element: `keyboard-input-cont`
 * - wrapper around input element: `keyboard-input-wrapper`
 * - the input element: `keyboard-input`
 * - container for backspace button: `keyboard-input-backspace-root`
 */
class KeyboardInput extends AutoFocusComponent {
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
    const { onInputChange, value, autoFocus } = this.props
    const inputNode = this.input
    if (!inputNode) {
      return
    }
    const { selectionStart, selectionEnd } = inputNode
    let nextValue
    let nextSelectionPosition
    if (selectionStart === selectionEnd) {
      nextValue = value.substring(0, selectionStart - 1) + value.substring(selectionEnd)
      nextSelectionPosition = selectionStart - 1
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
    onInputChange(event.target.value)
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

  render() {
    const { classes, onInputKeyUp, value, inputType, autoFocus } = this.props
    return (
      <div className={classes.keyboardInputRoot}>
        <div className={classes.keyboardInputCont}>
          <div className={classes.keyboardInputWrapper}>
            <input
              ref={(el) => (this.input = el)}
              onChange={this.handleInputChange}
              value={value}
              onKeyUp={onInputKeyUp}
              autoFocus={autoFocus}
              className={classes.keyboardInput}
              type={inputType}
            />
          </div>
          <div className={classes.keyboardInputBackspaceRoot} onClick={this.handleBackspaceClick}>
            <svg version="1.1" id="backspace" xmlns="http://www.w3.org/2000/svg" x="0px" y="0px"
              style={{ height: '100%', width: 'auto', display: 'block', boxSizing: 'border-box', float: 'right' }} viewBox="0 0 612 612"
            >
              <g>
                <g id="backspace">
                  <path d="M561,76.5H178.5c-17.85,0-30.6,7.65-40.8,22.95L0,306l137.7,206.55c10.2,12.75,22.95,22.95,40.8,22.95H561
                    c28.05,0,51-22.95,51-51v-357C612,99.45,589.05,76.5,561,76.5z M484.5,397.8l-35.7,35.7L357,341.7l-91.8,91.8l-35.7-35.7
                    l91.8-91.8l-91.8-91.8l35.7-35.7l91.8,91.8l91.8-91.8l35.7,35.7L392.7,306L484.5,397.8z"
                  />
                </g>
              </g>
            </svg>
          </div>
        </div>
      </div>
    )
  }
}

KeyboardInput.propTypes = {
  /**
   * Injected classes
   * @ignore
   */
  classes: PropTypes.object,
  /**
   * Called when input changes
   */
  onInputChange: PropTypes.func,
  /**
   * Called on input key up
   */
  onInputKeyUp: PropTypes.func,
  /**
   * Input value for controlled component
   */
  value: PropTypes.string.isRequired,
  /**
   * Input type
   */
  inputType: PropTypes.string,
  /**
   * Called to pass key pressed handler
   */
  onSetKeyPressedHandler: PropTypes.func,
  /**
   * Control autofocus property on the input
   */
  autoFocus: PropTypes.bool
}

KeyboardInput.defaultProps = {
  onInputChange: () => null,
  onInputKeyUp: () => null,
  autoFocus: true
}

export default injectSheet(styles)(KeyboardInput)
