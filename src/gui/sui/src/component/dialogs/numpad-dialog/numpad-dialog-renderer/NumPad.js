import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import _ from 'lodash'

import injectSheet, { jss } from 'react-jss'
import { AutoFocusComponent, ensureDecimals } from '3s-posui/utils'
import { NumpadKeys } from './StyledNumpad'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = (theme) => ({
  numPadRoot: {
    composes: 'numpad-root',
    backgroundColor: theme.popupsBackgroundColor,
    height: '100%',
    width: '100%'
  },
  numPadTable: {
    composes: 'numpad-table',
    borderCollapse: 'collapse',
    backgroundColor: theme.popupsBackgroundColor,
    '& td': {
      padding: 0
    },
    '& tr:nth-child(2) td': {
      paddingTop: '0.5vmin'
    },
    '& tr:last-child td': {
      paddingBottom: '0.5vmin'
    },
    '& tr td:first-child': {
      paddingLeft: '0.5vmin'
    },
    '& tr td:last-child': {
      paddingRight: '0.5vmin'
    },
    '& tr:nth-child(1) td': {
      padding: '0'
    }
  },
  numPadInputRoot: {
    composes: 'numpad-input-root',
    height: '100%'
  },
  numPadInputCont: {
    composes: 'numpad-input-cont',
    display: 'flex',
    alignItems: 'center',
    backgroundColor: theme.inputBackground,
    width: '100%',
    height: '20%',
    position: 'absolute'
  },
  numPadInputWrapper: {
    composes: 'numpad-input-wrapper',
    position: 'relative',
    paddingTop: '0.7vh',
    paddingBottom: '0.7vh',
    paddingLeft: '3%',
    flexGrow: 1,
    flexShrink: 1,
    flexBasis: '0',
    boxSizing: 'border-box'
  },
  numPadInput: {
    composes: 'numpad-input',
    width: '100%',
    fontSize: '4vmin',
    outline: 'none',
    border: 'none',
    fontWeight: 'bold',
    textAlign: 'right',
    fontFamily: 'sans-serif, monospace',
    backgroundColor: theme.inputBackground,
    '&::selection': {
      backgroundColor: 'black',
      color: 'white'
    },
    '&:placeholder-shown': {
      fontFamily: 'Arial Bold, Arial',
      fontWeight: 'normal',
      fontSize: '4vmin !important'
    }
  },
  numPadBackspaceRoot: {
    composes: 'numpad-backspace-root',
    position: 'relative',
    height: '100%',
    width: '100%',
    padding: '1vh 2%',
    flex: '0',
    color: theme.inputBackSpaceColor,
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    boxSizing: 'border-box'
  },
  numPadCurrencySymbol: {
    composes: 'numpad-currency-symbol',
    position: 'relative',
    padding: '0.7vmin 0 0.7vmin 2%',
    fontSize: '4.5vmin !important',
    flexGrow: 0,
    flexShrink: 0,
    flexBasis: '0',
    boxSizing: 'border-box'
  },
  numPadButton: {
    backgroundColor: theme.backgroundColor,
    fontWeight: 'normal',
    composes: 'numpad-button',
    border: 'none',
    width: '100%',
    height: '100%',
    fontSize: '4.5vmin !important',
    outline: 'none',
    '&:active': {
      backgroundColor: theme.pressedBackgroundColor,
      color: theme.pressedColor
    }
  }
})

class NumPad extends AutoFocusComponent {
  clearStyle = {}

  valueWithPoint = (value) => {
    const { l10n } = this.props
    const decimalSeparator = l10n.DECIMALS_SEPARATOR || '.'
    return (value || '').replace(new RegExp(`(\\${decimalSeparator})`, 'g'), '.')
  }

  handleChange = (event) => {
    if (!this.props.currencyMode && !this.props.numberMode) {
      this.props.onTextChange(String(event.target.value))
    }
  }

  formatValue = (props) => {
    const { l10n } = props
    const currencyDecimals = parseInt(l10n.CURRENCY_DECIMALS || 2, 10)

    let newValue = props.value
    if ((this.props.currencyMode || this.props.numberMode) && !currencyDecimals && newValue) {
      newValue = `${parseInt(newValue, 10)}`
    }

    if (newValue !== props.value) {
      this.props.onTextChange(newValue)
    }
  }

  handleButton = (value) => {
    const { currencyMode, numberMode, weightMode, shouldClearText, maxNumber, onTextChange } = this.props
    let newValue = ''
    if (currencyMode || numberMode || weightMode) {
      const currencyDecimals = currencyMode || numberMode ? 2 : 3

      if (!/^\d+$/.test(value)) {
        return
      }
      let currentValue = currencyMode || numberMode
        ? ensureDecimals(this.valueWithPoint(this.props.value))
        : this.props.value
      if (shouldClearText()) {
        currentValue = ensureDecimals('0', currencyDecimals)
      }
      currentValue = currentValue.replace(/\./g, '')
      currentValue += value
      const position = currentValue.length - currencyDecimals
      if (currencyMode || numberMode) {
        currentValue = ensureDecimals([currentValue.slice(0, position), currentValue.slice(position)].join('.'))
      } else {
        currentValue = [parseInt(currentValue.slice(0, position), 10), currentValue.slice(position)].join('.')
      }

      if (Number(currentValue) >= maxNumber) {
        return
      }
      newValue = currentValue
    } else {
      newValue = `${this.props.value}${value}`
    }

    onTextChange(newValue)
  }

  handleClear = (clearAll = false) => {
    const currencyDecimals = this.props.currencyMode || this.props.numberMode ? 2 : 3

    let newValue
    if (clearAll || this.props.shouldClearText()) {
      newValue = this.props.currencyMode || this.props.numberMode ? ensureDecimals('0') : ''
    } else if (!this.props.currencyMode && !this.props.numberMode && !this.props.weightMode) {
      newValue = this.props.value.slice(0, -1)
    } else if (this.props.weightMode) {
      let currentValue = this.props.value.slice(0, -1)
      currentValue = currentValue.replace(/\./g, '')
      if (currentValue.length < 4) {
        currentValue = '0'.repeat(4 - currentValue.length) + currentValue
      }
      const position = currentValue.length - currencyDecimals
      newValue = [parseInt(currentValue.slice(0, position), 10), currentValue.slice(position)].join('.')
    } else {
      const currentValue = Number(this.valueWithPoint(this.props.value)) / 10
      newValue = ensureDecimals(currentValue)
    }
    this.props.onTextChange(newValue)
  }

  handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      this.props.onEnterPressed()
      return
    }
    if (_.includes(['Delete', 'Backspace'], event.key)) {
      this.handleClear()
      return
    }
    if (event.key === 'Escape') {
      return
    }
    if (event.key === 'Unidentified') {
      if (event.which >= 48 && event.which < 58) {
        this.handleButton(`${event.which - 48}`)
      }
    } else {
      this.handleButton(event.key)
    }
  }

  handleBlur = () => {
    if (this.props.forceFocus && this.canForceFocus()) {
      this.numPadInput.focus()
    }
  }

  computeStyles = () => {
    const { styleButton, styleButtonClear } = this.props
    this.clearStyle = { ...styleButton, ...styleButtonClear }
  }

  componentDidUpdate(prevProps) {
    if (prevProps.value !== this.props.value) {
      this.formatValue(this.props)
    }
    if (prevProps.styleButton !== this.props.styleButton ||
      prevProps.styleButtonClear !== this.props.styleButtonClear) {
      this.computeStyles()
    }
  }

  componentDidMount = () => {
    this.formatValue(this.props)
    this.handleBlur()
  }

  render() {
    const {
      classes, className, style, styleTable, styleInputRoot, styleInputCont, styleCurrencySymbol,
      styleInput, styleInputCurrency, styleBackspaceRoot,
      suppressLogging, rounded, clearButtonText, currencyMode, weightMode, l10n, value, numberMode
    } = this.props
    const currencySymbol = l10n.CURRENCY_SYMBOL || '$'
    const weightSymbol = l10n.WEIGHT_SYMBOL || 'KG'
    let inputStyle = {
      ...styleInput,
      textAlign: this.props.textAlign
    }
    const currencyDecimals = parseInt(l10n.CURRENCY_DECIMALS || 2, 10)
    const decimalSeparator = l10n.DECIMALS_SEPARATOR || '.'
    if (!currencyMode) {
      inputStyle = {
        ...inputStyle,
        ...styleInputCurrency,
        left: '2%',
        width: '100%'
      }
    }

    const displayValue = (!(currencyMode || numberMode) || !currencyDecimals) ?
      value : ensureDecimals(this.valueWithPoint(value), currencyDecimals, decimalSeparator)

    return (
      <div className={`${classes.numPadRoot} ${className}`} style={style}>
        <table className={classes.numPadTable} style={{ ...styleTable, height: '100%', width: '100%' }}>
          <tbody>
            <tr style={{ height: '20%' }}>
              <td colSpan="3">
                <div className={classes.numPadInputRoot} style={styleInputRoot}>
                  <div className={classes.numPadInputCont} style={styleInputCont}>
                    {currencyMode &&
                      <div
                        className={classes.numPadCurrencySymbol}
                        style={styleCurrencySymbol}
                      >{currencySymbol}
                      </div>
                    }
                    {weightMode &&
                      <div
                        className={classes.numPadCurrencySymbol}
                      >{weightSymbol}
                      </div>
                    }
                    <div className={classes.numPadInputWrapper}>
                      <input
                        ref={(ref) => (this.numPadInput = ref)}
                        type={this.props.password ? 'password' : 'text'}
                        className={`${classes.numPadInput} test_NumPad_INPUT`}
                        placeholder={this.props.placeholder}
                        style={inputStyle}
                        onChange={this.handleChange}
                        onKeyDown={this.handleKeyDown}
                        value={displayValue}
                        autoFocus={this.props.forceFocus}
                        readOnly={true}
                        onBlur={this.handleBlur}
                      />
                    </div>
                    <div
                      className={classes.numPadBackspaceRoot}
                      style={styleBackspaceRoot}
                      onClick={() => this.handleClear()}
                    >
                      <i className="fas fa-backspace fa-2x" style={{ fontSize: '7vmin' }}/>
                    </div>
                  </div>
                </div>
              </td>
            </tr>
            <tr style={{ height: '20%' }}>
              <td style={{ width: '33.33%' }}>
                <NumpadKeys
                  suppressLogging={suppressLogging}
                  rounded={rounded}
                  onClick={() => this.handleButton('1')}
                  className={classes.numPadButton}
                  classNamePressed="numpad-button-pressed"
                >
                  1
                </NumpadKeys>
              </td>
              <td style={{ width: '33.33%' }}>
                <NumpadKeys
                  suppressLogging={suppressLogging}
                  rounded={rounded} onClick={() => this.handleButton('2')}
                  className={classes.numPadButton}
                  classNamePressed="numpad-button-pressed"
                >
                  2
                </NumpadKeys>
              </td>
              <td style={{ width: '33.33%' }}>
                <NumpadKeys
                  suppressLogging={suppressLogging}
                  rounded={rounded}
                  onClick={() => this.handleButton('3')}
                  className={classes.numPadButton}
                  classNamePressed="numpad-button-pressed"
                >
                  3
                </NumpadKeys>
              </td>
            </tr>
            <tr style={{ height: '20%' }}>
              <td>
                <NumpadKeys
                  suppressLogging={suppressLogging}
                  rounded={rounded}
                  onClick={() => this.handleButton('4')}
                  className={classes.numPadButton}
                  classNamePressed="numpad-button-pressed"
                >
                  4
                </NumpadKeys>
              </td>
              <td>
                <NumpadKeys
                  suppressLogging={suppressLogging}
                  rounded={rounded}
                  onClick={() => this.handleButton('5')}
                  className={classes.numPadButton}
                  classNamePressed="numpad-button-pressed"
                >
                  5
                </NumpadKeys>
              </td>
              <td>
                <NumpadKeys
                  suppressLogging={suppressLogging}
                  rounded={rounded}
                  onClick={() => this.handleButton('6')}
                  className={classes.numPadButton}
                  classNamePressed="numpad-button-pressed"
                >
                  6
                </NumpadKeys>
              </td>
            </tr>
            <tr style={{ height: '20%' }}>
              <td>
                <NumpadKeys
                  suppressLogging={suppressLogging}
                  rounded={rounded}
                  onClick={() => this.handleButton('7')}
                  className={classes.numPadButton}
                  classNamePressed="numpad-button-pressed"
                >
                  7
                </NumpadKeys>
              </td>
              <td>
                <NumpadKeys
                  suppressLogging={suppressLogging}
                  rounded={rounded}
                  onClick={() => this.handleButton('8')}
                  className={classes.numPadButton}
                  classNamePressed="numpad-button-pressed"
                >
                  8
                </NumpadKeys>
              </td>
              <td>
                <NumpadKeys
                  suppressLogging={suppressLogging}
                  rounded={rounded}
                  onClick={() => this.handleButton('9')}
                  className={classes.numPadButton}
                  classNamePressed="numpad-button-pressed"
                >
                  9
                </NumpadKeys>
              </td>
            </tr>
            <tr style={{ height: '20%' }}>
              <td>
                <NumpadKeys
                  rounded={rounded}
                  onClick={() => this.handleClear(true)}
                  className={`${classes.numPadButton} test_NumPad_CLEAR`}
                  classNamePressed="numpad-button-pressed numpad-button-clear-pressed"
                >
                  {clearButtonText}
                </NumpadKeys>
              </td>
              <td>
                <NumpadKeys
                  suppressLogging={suppressLogging}
                  rounded={rounded}
                  onClick={() => this.handleButton('0')}
                  className={classes.numPadButton}
                  classNamePressed="numpad-button-pressed"
                >
                  0
                </NumpadKeys>
              </td>
              <td>
                {this.props.showDoubleZero &&
                  <NumpadKeys
                    suppressLogging={this.props.suppressLogging}
                    rounded={rounded}
                    onClick={() => this.handleButton('00')}
                    className={classes.numPadButton}
                    classNamePressed="numpad-button-pressed"
                  >
                    00
                  </NumpadKeys>
                }
                {!this.props.showDoubleZero && this.props.children}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    )
  }
}

NumPad.propTypes = {
  classes: PropTypes.object,
  style: PropTypes.oneOfType([PropTypes.object, PropTypes.string]),
  styleTable: PropTypes.object,
  styleInputRoot: PropTypes.object,
  styleInputCont: PropTypes.object,
  styleInput: PropTypes.object,
  styleInputCurrency: PropTypes.object,
  styleCurrencySymbol: PropTypes.object,
  styleBackspaceRoot: PropTypes.object,
  className: PropTypes.string,
  clearButtonText: PropTypes.string,
  currencyMode: PropTypes.bool,
  numberMode: PropTypes.bool,
  weightMode: PropTypes.bool,
  maxNumber: PropTypes.number,
  maxLength: PropTypes.number,
  forceFocus: PropTypes.bool,
  showDoubleZero: PropTypes.bool,
  textAlign: PropTypes.string,
  onTextChange: PropTypes.func,
  placeholder: PropTypes.string,
  onEnterPressed: PropTypes.func,
  password: PropTypes.bool,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  shouldClearText: PropTypes.func,
  suppressLogging: PropTypes.bool,
  rounded: PropTypes.bool,
  l10n: PropTypes.object
}

NumPad.defaultProps = {
  style: {},
  styleTable: {},
  styleInputRoot: {},
  styleInputCont: {},
  styleCurrencySymbol: {},
  styleInput: {},
  styleInputCurrency: {},
  styleBackspaceRoot: {},
  className: '',
  clearButtonText: 'CLR',
  currencyMode: false,
  numberMode: false,
  weightMode: false,
  maxNumber: 9999999.99,
  maxLength: 15,
  forceFocus: false,
  placeholder: '',
  textAlign: 'left',
  onTextChange: (value) => value,
  onEnterPressed: () => null,
  password: false,
  shouldClearText: () => false,
  suppressLogging: false,
  rounded: true,
  l10n: {}
}

function mapStateToProps(state) {
  return {
    l10n: (state.locale || {}).l10n
  }
}

export default connect(mapStateToProps)(injectSheet(styles)(NumPad))
