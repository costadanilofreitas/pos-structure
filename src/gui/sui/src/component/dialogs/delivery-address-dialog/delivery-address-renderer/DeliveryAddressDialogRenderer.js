import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { cpf, cnpj } from 'cpf-cnpj-validator'

import { I18N } from '3s-posui/core'
import { FlexChild, FlexGrid } from '3s-widgets'
import {
  BottomButton,
  DeliveryAddressBackground,
  DeliveryAddressKeyboard,
  DeliveryAddressMainContainer,
  DeliveryAddressTitle,
  InputTitle,
  SearchButton,
  AddressInfoContainer,
  InputContainer,
  SearchButtonContainer
} from './StyledDeliveryAddressDialog'
import { IconStyle } from '../../../../constants/commonStyles'
import KeyboardWrapper from '../../keyboard-dialog/keyboard-dialog/KeyboardWrapper'
import MessageBusPropTypes from '../../../../prop-types/MessageBusPropTypes'
import OrderPropTypes from '../../../../prop-types/OrderPropTypes'
import KeyboardInput from '../../keyboard-dialog/keyboard-dialog/KeyboardInput'
import findCepInfo from '../../../../util/findCepInfo'


class DeliveryAddressDialogRenderer extends Component {
  constructor(props) {
    super(props)

    this.state = {
      inputDocument: props.order.CustomOrderProperties.CUSTOMER_DOC || '',
      inputPhoneNumber: props.order.CustomOrderProperties.CUSTOMER_PHONE || '',
      inputName: props.order.CustomOrderProperties.CUSTOMER_NAME || '',
      inputZipCode: props.order.CustomOrderProperties.POSTAL_CODE || '',
      inputCity: props.order.CustomOrderProperties.CITY || '',
      inputAddress: props.order.CustomOrderProperties.STREET_NAME || '',
      inputNeighborhood: props.order.CustomOrderProperties.NEIGHBORHOOD || '',
      inputNumber: props.order.CustomOrderProperties.STREET_NUMBER || '',
      inputComplement: props.order.CustomOrderProperties.COMPLEMENT || '',
      inputReference: props.order.CustomOrderProperties.ADDRESS_REFERENCE || '',
      currentInput: 'inputPhoneNumber',
      inputMasks: {
        inputPhoneNumber: '(99) 9999-9999',
        inputDocument: '999.999.999-999',
        inputZipCode: '99999-999'
      },
      invalidDocument: false
    }

    this.handleOnCancel = this.handleOnCancel.bind(this)
    this.handleInput = this.handleInput.bind(this)
    this.handleOnOk = this.handleOnOk.bind(this)
    this.handleInputClick = this.handleInputClick.bind(this)
    this.handleInputOnBlur = this.handleInputOnBlur.bind(this)
  }

  componentDidUpdate(prevProps, prevState) {
    if (prevState.inputPhoneNumber !== this.state.inputPhoneNumber) {
      if (this.state.inputPhoneNumber[5] === '9') {
        this.setState({ inputMasks: { ...prevState.inputMasks, inputPhoneNumber: '(99) 99999-9999' } })
      } else {
        this.setState({ inputMasks: { ...prevState.inputMasks, inputPhoneNumber: '(99) 9999-9999' } })
      }
    }
    if (prevState.inputDocument !== this.state.inputDocument) {
      if (this.state.inputDocument.length > 14) {
        this.setState({ inputMasks: { ...prevState.inputMasks, inputDocument: '99.999.999/9999-99' } })
      }
      if (this.state.inputDocument.length <= 14 && prevState.inputDocument.length > 14) {
        this.setState({ inputMasks: { ...prevState.inputMasks, inputDocument: '999.999.999-999' } })
      }
    }
  }

  handleInput = (input, state) => {
    this.setState({ [state]: input })
  }

  handleOnCancel() {
    this.props.closeDialog('{}')
  }

  handleOnOk() {
    const customer = {}
    this.createCustomer(customer)
    this.props.closeDialog(JSON.stringify(customer))
  }

  createCustomer(addressData) {
    const phone = this.state.inputPhoneNumber.replaceAll('(', '').replaceAll(')', '').replaceAll('-', '').replaceAll(' ', '')
    const document = this.state.inputDocument.replaceAll('-', '').replaceAll('.', '').replaceAll('/', '')
    const zipCode = this.state.inputZipCode.replaceAll('-', '')

    this.addCustomProperty(addressData, 'CUSTOMER_PHONE', phone)
    this.addCustomProperty(addressData, 'CUSTOMER_DOC', document)
    this.addCustomProperty(addressData, 'CUSTOMER_NAME', this.state.inputName)
    this.addCustomProperty(addressData, 'NEIGHBORHOOD', this.state.inputNeighborhood)
    this.addCustomProperty(addressData, 'COMPLEMENT', this.state.inputComplement)
    this.addCustomProperty(addressData, 'POSTAL_CODE', zipCode)
    this.addCustomProperty(addressData, 'STREET_NAME', this.state.inputAddress)
    this.addCustomProperty(addressData, 'ADDRESS_REFERENCE', this.state.inputReference)
    this.addCustomProperty(addressData, 'STREET_NUMBER', this.state.inputNumber)
    this.addCustomProperty(addressData, 'CITY', this.state.inputCity)
  }

  addCustomProperty(dictionary, key, value) {
    dictionary[key] = value
  }

  handleInputClick(input) {
    this.setState({ currentInput: input })
  }

  renderInput(inputId, i18n, value, size, mask, maskChange) {
    const showBorder = this.state.currentInput === inputId
    return (
      <DeliveryAddressKeyboard
        onClick={() => this.handleInputClick(inputId)}
      >
        <InputContainer direction={'row'}>
          <FlexChild size={2}>
            <InputTitle error={inputId === 'inputDocument' && this.state.invalidDocument}>
              <I18N id={i18n}/>
            </InputTitle>
          </FlexChild>
          <FlexChild
            size={size}
            style={{ borderBottom: showBorder ? '4px solid #525B81' : 'none' }}
          >
            <KeyboardInput
              value={value}
              mask={mask}
              beforeMaskedValueChange={maskChange}
              onSetKeyPressedHandler={this.handleKeyPressedKeyboard}
              onInputChange={(input) => this.handleInput(input, inputId)}
              flat={true}
              autoFocus={this.state.currentInput === inputId}
              paddingBackspace={true}
              onFocus={() => this.setState({ currentInput: inputId })}
              onBlur={() => this.handleInputOnBlur(inputId, value)}
              showBackspace={false}
            />
          </FlexChild>
        </InputContainer>
      </DeliveryAddressKeyboard>
    )
  }

  handleInputOnBlur(inputId, value) {
    if (inputId === 'inputDocument') {
      this.setState({ invalidDocument: (value !== '' && !cpf.isValid(value) && !cnpj.isValid(value)) })
    }

    this.setState({ currentInput: '' })
  }

  handleGetAddress() {
    const { inputZipCode } = this.state
    const { msgBus } = this.props

    msgBus.parallelSyncAction('zip_code_search')

    findCepInfo(inputZipCode).then((response) => {
      this.setState({
        inputCity: !response.erro ? response.localidade : '',
        inputAddress: !response.erro ? response.logradouro : '',
        inputNeighborhood: !response.erro ? response.bairro : ''
      })

      msgBus.parallelSyncAction('zip_code_search_finished')
    }).catch(() => {
      this.setState({
        inputCity: '',
        inputAddress: '',
        inputNeighborhood: ''
      })

      msgBus.parallelSyncAction('zip_code_search_finished', true)
    })
  }

  handleGetCustomer() {
    const { inputPhoneNumber } = this.state
    const { msgBus } = this.props

    const phone = inputPhoneNumber.replaceAll('(', '').replaceAll(')', '').replaceAll('-', '').replaceAll(' ', '')
    msgBus.parallelSyncAction('get_customer', phone).then(response => {
      if (response.ok && Object.keys(response.data).length > 0) {
        this.setState({
          inputDocument: response.data.document,
          inputName: response.data.name,
          inputZipCode: response.data.address.zip_code,
          inputCity: response.data.address.city,
          inputAddress: response.data.address.street,
          inputNeighborhood: response.data.address.neighborhood,
          inputNumber: response.data.address.number,
          inputComplement: response.data.address.complement,
          inputReference: response.data.address.reference_point
        })

        msgBus.parallelSyncAction('get_customer_search_finished')
      } else {
        this.cleanCustomerFields()
        msgBus.parallelSyncAction('get_customer_search_finished', true)
      }
    }).catch(() => {
      this.cleanCustomerFields()
      msgBus.parallelSyncAction('zip_code_search_finished', true)
    })
  }

  cleanCustomerFields() {
    this.setState({
      inputDocument: '',
      inputName: '',
      inputZipCode: '',
      inputCity: '',
      inputAddress: '',
      inputNeighborhood: '',
      inputNumber: '',
      inputComplement: '',
      inputReference: ''
    })
  }

  renderAddressTitle() {
    return (
      <FlexChild size={1}>
        <DeliveryAddressTitle>
          <I18N id={'$DELIVERY_INFO'}/>
        </DeliveryAddressTitle>
      </FlexChild>
    )
  }

  renderAddressInputs() {
    return (
      <AddressInfoContainer size={6}>
        <FlexGrid direction={'column'}>
          <FlexChild>
            <FlexGrid direction={'row'}>
              <FlexChild>
                <FlexGrid direction={'row'}>
                  <FlexChild size={4}>
                    {this.renderInput(
                      'inputPhoneNumber',
                      '$PHONE_DELIVERY_REPORT',
                      this.state.inputPhoneNumber,
                      4,
                      this.state.inputMasks.inputPhoneNumber
                    )
                    }
                  </FlexChild>
                  <SearchButtonContainer>
                    <SearchButton onClick={() => this.handleGetCustomer()} className={'fa fa-search fa-2x'}/>
                  </SearchButtonContainer>
                </FlexGrid>
              </FlexChild>
              <FlexChild>
                {this.renderInput(
                  'inputDocument',
                  '$CPF_CNPJ',
                  this.state.inputDocument,
                  5,
                  this.state.inputMasks.inputDocument
                )
                }
              </FlexChild>
            </FlexGrid>
          </FlexChild>
          <FlexChild>
            {this.renderInput('inputName', '$NAME', this.state.inputName, 13)}
          </FlexChild>
          <FlexChild>
            <FlexGrid direction={'row'}>
              <FlexChild>
                <FlexGrid>
                  <FlexChild size={4}>
                    {this.renderInput(
                      'inputZipCode',
                      '$ZIP_CODE',
                      this.state.inputZipCode,
                      4,
                      this.state.inputMasks.inputZipCode
                    )
                    }
                  </FlexChild>
                  <SearchButtonContainer>
                    <SearchButton onClick={() => this.handleGetAddress()} className={'fa fa-search fa-2x'}/>
                  </SearchButtonContainer>
                </FlexGrid>
              </FlexChild>
              <FlexChild>
                {this.renderInput('inputCity', '$CITY', this.state.inputCity, 5)}
              </FlexChild>
            </FlexGrid>
          </FlexChild>
          <FlexChild>
            {this.renderInput('inputAddress', '$ADDRESS', this.state.inputAddress, 13)}
          </FlexChild>
          <FlexChild>
            <FlexGrid direction={'row'}>
              <FlexChild>
                {this.renderInput('inputNeighborhood', '$NEIGHBORHOOD', this.state.inputNeighborhood, 5.5)}
              </FlexChild>
              <FlexChild>
                {this.renderInput('inputNumber', '$NUMBER', this.state.inputNumber, 5)}
              </FlexChild>
            </FlexGrid>
          </FlexChild>
          <FlexChild>
            <FlexGrid direction={'row'}>
              <FlexChild>
                {this.renderInput('inputComplement', '$COMPLEMENT_DELIVERY_REPORT', this.state.inputComplement, 5.5)}
              </FlexChild>
              <FlexChild>
                {this.renderInput('inputReference', '$REFERENCE_POINT', this.state.inputReference, 5)}
              </FlexChild>
            </FlexGrid>
          </FlexChild>
        </FlexGrid>
      </AddressInfoContainer>
    )
  }

  renderAddressKeyboard() {
    const mask = this.state.inputMasks[this.state.currentInput]
    return (
      <FlexChild size={4}>
        <DeliveryAddressKeyboard noInputWrapper={true}>
          <KeyboardWrapper
            handleOnInputChange={(input) => this.handleInput(input, this.state.currentInput)}
            showInput={false}
            value={this.state[this.state.currentInput]}
            keyboardVisible={true}
            showHideKeyboardButton={false}
            flat={true}
            autoFocus={false}
            mask={mask}
            onBlur={() => this.handleBlur(this.state.currentInput)}
            showBackspace={true}
          />
        </DeliveryAddressKeyboard>
      </FlexChild>
    )
  }

  renderAddressButtons() {
    const okButtonDisabled = this.state.invalidDocument

    return (
      <FlexChild size={1}>
        <FlexGrid>
          <BottomButton
            className={' test_DeliveryAddressDialog_CANCEL'}
            onClick={this.handleOnCancel}
          >
            <div>
              <IconStyle className="fa fa-ban fa-2x" aria-hidden="true" secondaryColor/>
            </div>
            <I18N id="$CANCEL"/>
          </BottomButton>
          <BottomButton
            className={' test_DeliveryAddressDialog_OK'}
            onClick={this.handleOnOk}
            disabled={okButtonDisabled}
          >
            <div>
              <IconStyle
                className="fa fa-check fa-2x"
                aria-hidden="true"
                secondaryColor={!okButtonDisabled}
                disabled={okButtonDisabled}
              />
            </div>
            <I18N id="$OK"/>
          </BottomButton>
        </FlexGrid>
      </FlexChild>
    )
  }

  render() {
    return (
      <DeliveryAddressBackground>
        <DeliveryAddressMainContainer>
          <FlexGrid direction={'column'}>
            {this.renderAddressTitle()}
            {this.renderAddressInputs()}
            {this.renderAddressKeyboard()}
            {this.renderAddressButtons()}
          </FlexGrid>
        </DeliveryAddressMainContainer>
      </DeliveryAddressBackground>
    )
  }
}

DeliveryAddressDialogRenderer.propTypes = {
  closeDialog: PropTypes.func,
  msgBus: MessageBusPropTypes,
  order: OrderPropTypes
}

export default DeliveryAddressDialogRenderer
