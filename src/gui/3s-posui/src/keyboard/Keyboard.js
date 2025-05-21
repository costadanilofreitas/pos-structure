import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import injectSheet, { jss } from 'react-jss'
import KeyboardButton from './KeyboardButton'
import LatinLayout from './layouts/LatinLayout'
import CyrillicLayout from './layouts/CyrillicLayout'
import SymbolsLayout from './layouts/SymbolsLayout'
import LanguageIcon from './icons/LanguageIcon'
import ShiftIcon from './icons/ShiftIcon'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = (theme) => ({
  keyboardRoot: {
    composes: 'keyboard-root',
    width: '95%',
    margin: '0 auto',
    height: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  keyboardLetters: {
    width: '100%',
    flex: 3,
    composes: 'keyboard-letters',
    float: 'left'
  },
  keyboardNumbersBox: {
    width: '100%',
    flex: 1,
    display: 'flex'
  },
  keyboardLetter: {
    composes: 'keyboard-letter',
    ...(theme.keyboardButton || {}),
    ...(theme.keyboardButtonLetter || {})
  },
  keyboardNumbers: {
    composes: 'keyboard-numbers',
    width: '24%',
    marginLeft: '1%',
    float: 'right',
    flex: 1
  },
  keyboardNumberButton: {
    composes: 'keyboard-number-button',
    flexGrow: 1,
    '&.button_0': {
      width: '17vw'
    },
    ...(theme.keyboardButton || {}),
    ...(theme.keyboardButtonNumber || {})
  },
  keyboardRow: {
    composes: 'keyboard-row',
    display: 'flex'
  },
  keyboardHalfButton: {
    composes: 'keyboard-half-button',
    flexBasis: '56px'
  },
  keyboardSpace: {
    composes: 'keyboard-space',
    flexGrow: 1,
    ...(theme.keyboardButton || {}),
    ...(theme.keyboardButtonSpace || {})
  },
  keyboardBackspace: {
    width: '25% !important',
    color: theme.pressedBackgroundColor,
    display: 'flex !important',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '0  !important',
    '&:before': {
      fontSize: '5vmin'
    }
  }
})

/**
 * Helper keyboard component that can be used in conjunction with `KeyboardInput` in order
 * to implement an on-screen keyboard suitable for POS touchscreen.
 *
 * Available class names:
 * - main container element: `keyboard-root`
 * - container for letters elements: `keyboard-letters`
 * - class for letter buttons: `keyboard-letters`
 * - container for numbers elements: `keyboard-numbers`
 * - class for number buttons: `keyboard-number-button`
 * - class for row element: `keyboard-row`
 * - helper element to shift a row: `keyboard-half-button`
 * - class for space button: `keyboard-space`
 */
class Keyboard extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      currentLayout: 0,
      showSymbols: false,
      uppercase: this.isUppercase(),
      capsLock: this.props.startWithCaps
    }
  }

  handleLanguageClick = () => {
    this.setState({
      currentLayout: (this.state.currentLayout + 1) % this.props.layouts.length,
      showSymbols: false
    })
  }

  handleShiftClick = () => {
    if (this.state.capsLock) {
      this.setState({ capsLock: false })
      return
    }
    this.setState({ uppercase: !this.state.uppercase })
  }

  handleCapsLockClick = () => {
    this.setState({ capsLock: !this.state.capsLock })
  }

  handleSymbolsClick = () => {
    this.setState({ showSymbols: !this.state.showSymbols })
  }

  getKeys() {
    let keysSet
    if (this.state.showSymbols) {
      keysSet = SymbolsLayout.layout
    } else {
      keysSet = this.props.layouts[this.state.currentLayout].layout
    }

    return (this.state.uppercase || this.state.capsLock) ?
      keysSet.map(keyRow => keyRow.map(key => key.toUpperCase()))
      : keysSet
  }

  getSymbolsKeyValue() {
    if (this.state.showSymbols) {
      return this.props.layouts[this.state.currentLayout].symbolsKeyValue
    }
    return SymbolsLayout.symbolsKeyValue
  }

  isUppercase() {
    const { inputType, isFirstLetterUppercase, value } = this.props
    return inputType !== 'password' &&
      inputType !== 'email' &&
      value &&
      !value.length &&
      isFirstLetterUppercase
  }

  render() {
    const {
      leftButtons, rightButtons, classes, inputType, onKeyPressed, rounded,
      buttonClassName, buttonClassNamePressed, showAt, showNumbers, showBackspace
    } = this.props
    const keys = this.getKeys()
    const numbers = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [0, '.']]

    return (
      <div className={classes.keyboardRoot}>
        <div className={classes.keyboardLetters}>
          <div className={classes.keyboardRow}>
            {keys[0].map(button =>
              <KeyboardButton
                value={button}
                onClick={onKeyPressed}
                key={button}
                rounded={rounded}
                className={`${classes.keyboardLetter} ${buttonClassName}`}
                classNamePressed={buttonClassNamePressed}
              />
            )}
          </div>

          <div className={classes.keyboardRow}>
            {keys[1].map(button =>
              <KeyboardButton
                value={button}
                onClick={onKeyPressed}
                key={button}
                rounded={rounded}
                className={`${classes.keyboardLetter} ${buttonClassName}`}
                classNamePressed={buttonClassNamePressed}
              />
            )}
          </div>

          <div className={classes.keyboardRow}>
            {this.props.showShift &&
              <KeyboardButton
                value={<ShiftIcon />}
                onClick={this.handleShiftClick}
                rounded={rounded}
                className={`${classes.keyboardLetter} ${buttonClassName}`}
                classNamePressed={buttonClassNamePressed}
              />
            }
            {keys[2].map(button =>
              <KeyboardButton
                value={button}
                onClick={onKeyPressed}
                key={button}
                rounded={rounded}
                className={`${classes.keyboardLetter} ${buttonClassName}`}
                classNamePressed={buttonClassNamePressed}
              />
            )}
          </div>

          <div className={classes.keyboardRow}>
            {leftButtons}
            {(this.props.layouts.length > 1) && (
              <KeyboardButton
                value={<LanguageIcon />}
                onClick={this.handleLanguageClick}
                rounded={rounded}
                className={`${classes.keyboardLetter} ${buttonClassName}`}
                classNamePressed={buttonClassNamePressed}
              />
            )}
            {showAt && (
              <KeyboardButton
                value={'@'}
                onClick={onKeyPressed}
                rounded={rounded}
                className={`${classes.keyboardLetter} ${buttonClassName}`}
                classNamePressed={buttonClassNamePressed}
              />
            )}
            <KeyboardButton
              value={' '}
              onClick={onKeyPressed}
              rounded={rounded}
              className={`${classes.keyboardSpace} ${buttonClassName}`}
              classNamePressed={buttonClassNamePressed}
            />
            {inputType === 'email' ?
              <KeyboardButton
                value={'.'}
                onClick={onKeyPressed}
                rounded={rounded}
                className={`${classes.keyboardLetter} ${buttonClassName}`}
                classNamePressed={buttonClassNamePressed}
              />
              : null}
            {showBackspace ?
              <KeyboardButton
                value={'backspace'}
                onClick={onKeyPressed}
                rounded={rounded}
                className={`${classes.keyboardBackspace} ${buttonClassName} fas fa-backspace fa-2x`}
                classNamePressed={buttonClassNamePressed}
              />
              : null}
            {rightButtons}
          </div>
        </div>
        { showNumbers &&
        <div className={classes.keyboardNumbersBox}>
          <div className={classes.keyboardNumbers}>
            <div className={classes.keyboardRow}>
              {numbers[0].map(button =>
                <KeyboardButton
                  value={button}
                  onClick={onKeyPressed}
                  key={button}
                  rounded={rounded}
                  className={`${classes.keyboardNumberButton} button_${button} ${buttonClassName}`}
                  classNamePressed={buttonClassNamePressed}
                />
              )}
            </div>
            <div className={classes.keyboardRow}>
              {numbers[1].map(button =>
                <KeyboardButton
                  value={button}
                  onClick={onKeyPressed}
                  key={button}
                  rounded={rounded}
                  className={`${classes.keyboardNumberButton} button_${button} ${buttonClassName}`}
                  classNamePressed={buttonClassNamePressed}
                />
              )}
            </div>
            <div className={classes.keyboardRow}>
              {numbers[2].map(button =>
                <KeyboardButton
                  value={button}
                  onClick={onKeyPressed}
                  key={button}
                  rounded={rounded}
                  className={`${classes.keyboardNumberButton} button_${button} ${buttonClassName}`}
                  classNamePressed={buttonClassNamePressed}
                />
              )}
            </div>
            <div className={classes.keyboardRow}>
              {numbers[3].map(button =>
                <KeyboardButton
                  value={`${button}`}
                  onClick={onKeyPressed}
                  key={`keyboard_button_${button}`}
                  rounded={rounded}
                  className={`${classes.keyboardNumberButton} button_${button} ${buttonClassName}`}
                  classNamePressed={buttonClassNamePressed}
                />
              )}
            </div>
          </div>
        </div>
        }
      </div>
    )
  }
}

Keyboard.propTypes = {
  /**
   * Injected classes
   * @ignore
   */
  classes: PropTypes.object,
  /**
   * Current input value
   */
  value: PropTypes.string.isRequired,
  /**
   * Additional buttons to display on the left
   */
  leftButtons: PropTypes.arrayOf(PropTypes.node),
  /**
   * Additional buttons to display on the right
   */
  rightButtons: PropTypes.arrayOf(PropTypes.node),
  /**
   * Callback called whenever a key is pressed
   */
  onKeyPressed: PropTypes.func,
  /**
   * Keyboard layouts to use
   */
  layouts: PropTypes.arrayOf(PropTypes.shape({
    symbolsKeyValue: PropTypes.string,
    layout: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.string))
  })),
  /**
   * Whether caps locks must be pressed or not by default
   */
  startWithCaps: PropTypes.bool,
  /**
   * Whether or not display shift button
   */
  showShift: PropTypes.bool,
  /**
   * Input type, currently accepted types are: 'text', 'password' and 'email'
   */
  inputType: PropTypes.string,
  /**
   * Indicates if first letter must be uppercase
   */
  isFirstLetterUppercase: PropTypes.bool,
  /**
   * Whether buttons should have rounded corners or not
   */
  rounded: PropTypes.bool,
  /**
   * Button class name
   */
  buttonClassName: PropTypes.string,
  /**
   * Button class name when pressed
   */
  buttonClassNamePressed: PropTypes.string,
  showAt: PropTypes.bool,
  showNumbers: PropTypes.bool,
  showBackspace: PropTypes.bool
}

Keyboard.defaultProps = {
  leftButtons: [],
  rightButtons: [],
  layouts: [CyrillicLayout, LatinLayout],
  startWithCaps: false,
  showShift: false,
  isFirstLetterUppercase: false,
  buttonClassName: '',
  buttonClassNamePressed: '',
  showAt: true,
  showNumbers: true,
  showBackspace: false
}

export default injectSheet(styles)(Keyboard)
