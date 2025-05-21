import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { I18N } from '3s-posui/core'
import NumPad from './NumPad'
import {
  AbsoluteWrapper,
  Numpad,
  NumpadBackground,
  NumpadBoxTitle,
  NumpadBoxTitleContainer,
  NumpadTitle,
  NumpadTitleText,
  NumpadButtons,
  NumpadContainer
} from './StyledNumpad'
import { IconStyle, PopupStyledButton } from '../../../../constants/commonStyles'
import { isEnter, isEsc } from '../../../../util/keyboardHelper'
import ScreenOrientation from '../../../../constants/ScreenOrientation'
import withState from '../../../../util/withState'

class NumpadDialogRenderer extends Component {
  constructor(props) {
    super(props)

    let initialValue = this.props.default
    if (initialValue == null || initialValue === '') {
      if (props.mask && props.mask.toLowerCase() === 'currency') {
        initialValue = '0.00'
      }
      if (props.mask && props.mask.toLowerCase() === 'date') {
        initialValue = this.getInicialDate(initialValue)
      }
    }
    this.state = {
      value: initialValue,
      visible: true
    }

    this.handleInputChange = this.handleInputChange.bind(this)
    this.handleOnOk = this.handleOnOk.bind(this)
    this.handleOnCancel = this.handleOnCancel.bind(this)
    this.handleKeyPressed = this.handleKeyPressed.bind(this)
  }

  render() {
    const { mask, type } = this.props
    const { visible, value } = this.state

    if (!visible) {
      return null
    }

    let currentValue = value
    const isDate = mask.toString().toLocaleLowerCase() === 'date'
    const isNumber = mask.toString().toLocaleLowerCase() === 'number'
    const isWeight = mask.toString().toLocaleLowerCase() === 'weight'
    const isCpfCnpj = mask.toString().toLocaleLowerCase() === 'cpf_cnpj'
    let isPassword = type === 'numpad_password' || type === 'password'
    const hideCancelButton = mask.toString().toLocaleLowerCase() !== 'no_cancel'
    if (mask.toString().toLocaleLowerCase() === 'password') {
      isPassword = true
    }

    if (isCpfCnpj) {
      currentValue = this.onlyDigits(currentValue)
      if (currentValue.length <= 11) {
        currentValue = this.cpfMask(currentValue)
      } else {
        currentValue = this.cnpjMask(currentValue)
      }
    } else if (isWeight) {
      currentValue = this.weightMask(currentValue)
    }

    return (
      <NumpadBackground flat={this.props.flatStyle}>
        <Numpad screenOrientation={this.props.screenOrientation} flat={this.props.flatStyle} mobile={this.props.mobile}>
          <NumpadBoxTitleContainer>
            <NumpadBoxTitle flat={this.props.flatStyle}>
              <NumpadTitle flat={this.props.flatStyle}>
                <NumpadTitleText><I18N id={this.props.title}/></NumpadTitleText>
                <NumpadTitleText><I18N id={this.props.message}/></NumpadTitleText>
              </NumpadTitle>
            </NumpadBoxTitle>
          </NumpadBoxTitleContainer>
          <NumpadContainer flat={this.props.flatStyle} screenOrientation={this.props.screenOrientation}>
            <AbsoluteWrapper style={{ display: 'flex' }} flat={this.props.flatStyle}>
              <AbsoluteWrapper flat={this.props.flatStyle} className={'test_NumPadDialog_CONTAINER'}>
                <NumPad
                  value={currentValue}
                  onTextChange={this.handleInputChange}
                  showDoubleZero={!isDate}
                  forceFocus={true}
                  password={isPassword}
                  supressLogging={isPassword}
                  numberMode={isNumber}
                  weightMode={isWeight}
                  styleCurrencySymbol={{ height: this.props.screenOrientation === ScreenOrientation.Portrait ? '70%' : '84%' }}
                  styleInputCont={{ borderRadius: this.props.flatStyle ? 'none' : '0.9vmin' }}
                  currencyMode={mask.toString().toLocaleLowerCase() === 'currency'}
                />
              </AbsoluteWrapper>
            </AbsoluteWrapper>
          </NumpadContainer>
          <NumpadButtons flat={this.props.flatStyle}>
            {hideCancelButton &&
            <PopupStyledButton
              active={true}
              flexButton={true}
              borderRight={true}
              flat={this.props.flatStyle}
              className={'test_NumPadDialog_CANCEL'}
              onClick={this.handleOnCancel}
            >
              <IconStyle className="fa fa-ban fa-2x" aria-hidden="true" totem={!this.props.flatStyle} secondaryColor={true}/>
              <I18N id="$CANCEL"/>
            </PopupStyledButton>
            }
            <PopupStyledButton
              active={true}
              flexButton={true}
              flat={this.props.flatStyle}
              style
              className={'test_NumPadDialog_OK'}
              onClick={this.handleOnOk}
              disabled={this.props.blockEmptyValue && this.state.value === ''}
              inlineText={true}
            >
              <IconStyle className="fa fa-check fa-2x" aria-hidden="true" totem={!this.props.flatStyle} secondaryColor={true}/>
              <I18N id="$OK"/>
            </PopupStyledButton>
          </NumpadButtons>
        </Numpad>
      </NumpadBackground>
    )
  }

  componentDidMount() {
    document.addEventListener('keydown', this.handleKeyPressed, false)
  }

  componentWillUnmount() {
    document.removeEventListener('keydown', this.handleKeyPressed, false)
  }

  handleInputChange = (value) => {
    const { mask } = this.props
    let retValue = value
    if (mask.toString().toLocaleLowerCase() === 'date') {
      if (value.length > 8) {
        return
      }
      retValue = this.removeSlashInDate(value)

      if (retValue === this.removeSlashInDate(this.state.value)) {
        retValue = retValue.substr(0, retValue.length - 1)
      }
    } else if (mask.toString().toLocaleLowerCase() === 'cpf_cnpj') {
      retValue = this.onlyDigits(retValue)

      if (retValue.length > 14) {
        return
      }
    }

    if (!isNaN(retValue)) {
      if (mask.toString().toLocaleLowerCase() === 'date') {
        retValue = this.insertSlashInDate(retValue)
      } else if (mask.toString().toLocaleLowerCase() === 'cpf_cnpj') {
        if (retValue.length <= 11) {
          retValue = this.cpfMask(retValue)
        } else {
          retValue = this.cnpjMask(retValue)
        }
      }
      this.setState({ value: retValue })
    }
  }

  removeSlashInDate(value) {
    let retValue = value
    if (value === value.substring(0, value.length) && value.endsWith('/')) {
      retValue = value.substring(0, value.length - 1)
    }

    retValue = retValue.replace(/\//g, '')
    return retValue
  }

  insertSlashInDate(value) {
    let retValue = value
    if (value.length >= 2) {
      retValue = `${value.substring(0, 2)}/${value.substring(2)}`
    }
    if (value.length >= 5) {
      retValue = `${value.substring(0, 2)}/${value.substring(2, 4)}/${value.substring(4)}`
    }
    return retValue
  }

  onlyDigits(value) {
    return value.replace(/\D/g, '')
  }

  handleOnOk() {
    const { mask, blockEmptyValue } = this.props
    let value = this.state.value
    if (blockEmptyValue && value === '') {
      return
    }

    const valueIsCpfOrCnpj = mask.toString().toLocaleLowerCase() === 'cpf_cnpj'
    const valueIsInteger = mask.toString().toLocaleLowerCase() === 'integer'
    const valueIsPassword = mask.toString().toLocaleLowerCase() === 'password'
    const valueIsDate = mask.toString().toLocaleLowerCase() === 'date'

    if (valueIsDate) {
      if (value.length !== 8) {
        return
      }

      value = value.replace(/\//g, '')
      const year = (parseInt(value.substring(4, 6), 10) + 2000).toString()
      const month = value.substring(2, 4)
      const day = value.substring(0, 2)

      value = year + month + day
    }

    if (valueIsCpfOrCnpj || valueIsInteger || valueIsPassword) {
      value = this.onlyDigits(value)
    }

    if (valueIsInteger && value !== '') {
      value = parseInt(value, 10)
    }

    if (this.props.closeDialog != null) {
      this.props.closeDialog('0', value)
    } else if (this.props.onDialogClose != null) {
      this.props.onDialogClose(value)
    }
  }

  handleOnCancel() {
    if (this.props.closeDialog != null) {
      this.props.closeDialog('-1')
    } else if (this.props.onDialogClose != null) {
      this.props.onDialogClose(0)
    }
  }

  handleKeyPressed(event) {
    if (isEnter(event)) {
      this.handleOnOk()
    }
    if (isEsc(event)) {
      this.handleOnCancel()
    }
  }

  getInicialDate() {
    let initialValue = new Date()
    const year = initialValue.getFullYear().toString().substring(2, 4)
    let month = initialValue.getMonth() + 1
    let day = initialValue.getDate()

    if (day < 10) {
      day = `0${day}`
    }
    if (month < 10) {
      month = `0${month}`
    }

    initialValue = `${day}/${month}/${year}`
    return initialValue
  }

  cpfMask(value) {
    return value
      .replace(/\D/g, '')
      .replace(/(\d{3})(\d)/, '$1.$2')
      .replace(/(\d{3})(\d)/, '$1.$2')
      .replace(/(\d{3})(\d{1,2})/, '$1-$2')
      .replace(/(-\d{2})\d+?$/, '$1')
  }

  cnpjMask(value) {
    return value
      .replace(/\D/g, '')
      .replace(/^(\d{2})(\d)/, '$1.$2')
      .replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3')
      .replace(/\.(\d{3})(\d)/, '.$1/$2')
      .replace(/(\d{4})(\d)/, '$1-$2')
  }

  weightMask(value) {
    return value.replace(new RegExp('(\\.)', 'g'), '.')
  }
}

NumpadDialogRenderer.propTypes = {
  flatStyle: PropTypes.bool,
  type: PropTypes.string,
  message: PropTypes.string,
  closeDialog: PropTypes.func,
  title: PropTypes.string,
  mask: PropTypes.string,
  default: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onDialogClose: PropTypes.func,
  mobile: PropTypes.bool,
  screenOrientation: PropTypes.number,
  blockEmptyValue: PropTypes.bool
}

NumpadDialogRenderer.defaultProps = {
  flatStyle: true,
  blockEmptyValue: false
}

export default (withState(NumpadDialogRenderer, 'mobile'))

