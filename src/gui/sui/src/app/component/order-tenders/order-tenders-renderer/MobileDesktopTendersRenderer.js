import React, { Component } from 'react'
import PropTypes from 'prop-types'
import _get from 'lodash/get'
import isEmpty from 'lodash/isEmpty'

import { I18N } from '3s-posui/core'
import { ensureArray, ensureDecimals } from '3s-posui/utils'
import { FlexChild, FlexGrid } from '3s-widgets'

import { isTefPaymentType } from './OrderTendersUtil'

import { IconStyle, CommonStyledButton } from '../../../../constants/commonStyles'
import OrderPropTypes from '../../../../prop-types/OrderPropTypes'
import TablePropTypes from '../../../../prop-types/TablePropTypes'
import TenderType from '../../../model/TenderType'
import RealBills from '../../real-bills'
import OperatorPropTypes from '../../../../prop-types/OperatorPropTypes'
import { NumPad } from '../../../../component/dialogs/numpad-dialog'
import DialogType from '../../../../constants/DialogType'
import StaticConfigPropTypes from '../../../../prop-types/StaticConfigPropTypes'
import DeviceType from '../../../../constants/Devices'
import ButtonGrid from '../../button-grid/ButtonGrid'

function getRootTenderTypes(tenderTypes, saleType, showTef = true) {
  let rootTenderTypes = tenderTypes.filter(function (tenderType) {
    if (tenderType.parentId != null) {
      return false
    }

    if (isTefPaymentType(tenderType)) {
      return showTef
    }

    if (saleType === 'DELIVERY') {
      return tenderType.showInDL || tenderType.showInFC
    }

    return tenderType.showInFC
  })

  if (saleType === 'DELIVERY') {
    const rootTenderTypesDL = rootTenderTypes.filter(function (tenderType) {
      return tenderType.showInDL
    })
    const rootTenderTypesFC = rootTenderTypes.filter(function (tenderType) {
      return tenderType.showInFC
    })

    rootTenderTypes = rootTenderTypesDL.concat(rootTenderTypesFC)
  }

  return rootTenderTypes
}

export default class MobileDesktopTendersRenderer extends Component {
  constructor(props) {
    super(props)

    const dueAmount = this.props.order['@attributes'].dueAmount
    const valueToPay = ensureDecimals(Number(dueAmount || '0'))
    this.otherPaymentsOptions = []
    this.state = {
      dueAmount,
      valueToPay,
      value: valueToPay
    }
    this.currentValue = valueToPay
    this.selectedPaymentType = null
    this.mobileDeviceType = ''

    this.handleInputChange = this.handleInputChange.bind(this)
    this.applyDiscounts = this.applyDiscounts.bind(this)
    this.cleanDiscounts = this.cleanDiscounts.bind(this)
    this.handlePaymentResponse = this.handlePaymentResponse.bind(this)
    this.processOtherPayments = this.processOtherPayments.bind(this)
    this.handleDeviceTypeResponse = this.handleDeviceTypeResponse.bind(this)
  }

  static getDerivedStateFromProps(props, state) {
    const dueAmount = parseFloat(props.order['@attributes'].dueAmount)
    const dueAmountNext = dueAmount < 0 ? 0 : dueAmount.toString()
    const nextDue = ensureDecimals(Number(dueAmountNext || '0'))
    const nextState = {}

    if (nextDue !== state.valueToPay) {
      nextState.valueToPay = nextDue
      nextState.value = nextDue
      nextState.clearCurrentText = true
    }

    nextState.dueAmount = dueAmountNext

    return nextState
  }

  componentDidMount() {
    if (window.mwapi != null) {
      window.processPaymentCallback = this.handlePaymentResponse
      window.getDeviceTypeCallback = this.handleDeviceTypeResponse

      window.mwapi.getDeviceType('getDeviceTypeCallback')
    }
  }

  handleDeviceTypeResponse(resultCode, message, payload) {
    if (resultCode === '0') {
      this.mobileDeviceType = payload
    }
  }

  render() {
    const { value } = this.state
    const { selectedTenderDivisionValue, staticConfig, deviceType } = this.props
    const { tenderTypes, billPaymentEnabled } = staticConfig

    this.currentValue = selectedTenderDivisionValue !== '0' ? selectedTenderDivisionValue : value
    const orderIsPaid = parseFloat(this.state.dueAmount) === 0
    const paymentButtonsDisabled = orderIsPaid || this.currentValue === '0.00'
    const payButtonsCols = 4
    const payButtonsRows = 2
    const payButtons = this.createPaymentButton(payButtonsCols, payButtonsRows, tenderTypes, paymentButtonsDisabled)
    const showRealBills = deviceType === DeviceType.Desktop

    return (
      <FlexGrid direction={'column'}>
        <FlexChild size={5}>
          <NumPad
            value={this.currentValue}
            onTextChange={this.handleInputChange}
            forceFocus={true}
            showDoubleZero={true}
            currencyMode={true}
            textAlign="right"
            shouldClearText={this.shouldClearText}
            style={{ backgroundColor: 'white' }}
          />
        </FlexChild>
        <FlexChild size={3}>
          <FlexGrid direction={'column'}>
            {showRealBills &&
            <FlexChild>
              <RealBills
                {...this.props}
                selectedSeats={Object.assign({}, this.props.selectedSeats)}
                disabled={orderIsPaid || !billPaymentEnabled}
              />
            </FlexChild>
            }
            <FlexChild size={2}>
              <ButtonGrid
                direction="row"
                cols={payButtonsCols}
                rows={payButtonsRows}
                buttons={Object.assign({}, payButtons)}
                style={{ position: 'relative' }}
              />
            </FlexChild>
          </FlexGrid>
        </FlexChild>
      </FlexGrid>
    )
  }

  createPaymentButton(payButtonsCols, payButtonsRows, tenderTypes, paymentButtonsDisabled) {
    const { showTef, staticConfig, saleType, order } = this.props
    const currentSaleType = (saleType || order.saleTypeDescr || 'FC').toString()
    const orderHasPayment = !isEmpty(_get(this.props, 'order.TenderHistory.Tender'))

    const rootTenderTypes = getRootTenderTypes(tenderTypes, currentSaleType, showTef)

    const otherPayments = rootTenderTypes.filter(function (tenderType) {
      return (tenderType.id > 2)
    })

    this.otherPaymentsOptions = []
    for (let i = 0; i < otherPayments.length; i++) {
      this.otherPaymentsOptions.push(otherPayments[i].id)
    }

    const defaultPaymentsQuantity = rootTenderTypes.length - otherPayments.length
    let otherPaymentsIndex = 0
    const paymentTypeSpacesQuantity = (payButtonsCols * payButtonsRows) - 2 - defaultPaymentsQuantity
    let showOtherPayments = false

    const payButtons = []
    for (let i = 0; i < ((payButtonsCols * payButtonsRows) - 1); i++) {
      if (i < rootTenderTypes.length && i < (payButtonsCols * payButtonsRows)) {
        if (rootTenderTypes[i].id === 0) {
          payButtons.push(
            this.createPaymentType(
              '$CASH',
              'fas fa-dollar-sign fa-2x',
              () => this.cashPayment(rootTenderTypes[i].id),
              null,
              paymentButtonsDisabled || !staticConfig.cashPaymentEnabled
            )
          )
          this.removeFromOtherPayments(rootTenderTypes, i)
        } else if (rootTenderTypes[i].id === 1) {
          payButtons.push(
            this.createPaymentType(
              '$CREDIT',
              'far fa-credit-card fa-2x',
              null,
              null,
              paymentButtonsDisabled,
              () => this.tefPayment(rootTenderTypes[i].id)
            )
          )
          this.removeFromOtherPayments(rootTenderTypes, i)
        } else if (rootTenderTypes[i].id === 2) {
          payButtons.push(
            this.createPaymentType(
              '$DEBIT',
              'fas fa-credit-card fa-2x',
              null,
              null,
              paymentButtonsDisabled,
              () => this.tefPayment(rootTenderTypes[i].id)
            )
          )
          this.removeFromOtherPayments(rootTenderTypes, i)
        } else if (rootTenderTypes[i].id === 50) {
          payButtons.push(
            this.createPaymentType(
              '$MERCADO_PAGO',
              'fas fa-mobile-alt fa-2x',
              null,
              null,
              paymentButtonsDisabled,
              () => this.tefPayment(rootTenderTypes[i].id)
            )
          )
          this.removeFromOtherPayments(rootTenderTypes, i)
        } else {
          let icon = ''
          try {
            switch (rootTenderTypes[i].descr.toLowerCase()) {
              case 'pagseguro':
                icon = 'far fa-credit-card fa-2x'
                break
              case 'ifood qrcode':
                icon = 'fas fa-qrcode fa-2x'
                break
              case 'peixe urbano':
                icon = 'fas fa-fish fa-2x'
                break
              case 'giftcard':
                icon = 'fas fa-gift fa-2x'
                break
              case 'delivery':
                icon = 'fas fa-motorcycle fa-2x'
                break
              default:
                break
            }
          } catch (e) {
            console.warn(e)
          }

          if (otherPayments <= paymentTypeSpacesQuantity || otherPaymentsIndex < paymentTypeSpacesQuantity - 1) {
            payButtons.push(
              this.createPaymentType(
                rootTenderTypes[i].descr,
                icon,
                () => this.externalPayment(rootTenderTypes[i].id),
                null,
                paymentButtonsDisabled
              )
            )
            this.removeFromOtherPayments(rootTenderTypes, i)
          } else {
            showOtherPayments = true
          }
          otherPaymentsIndex++
        }
      } else {
        payButtons.push(
          <CommonStyledButton disabled={true} border={true}>
            <i className={'fa fa-minus fa-2x'} aria-hidden="true" style={{ margin: '0.5vh' }}/>
          </CommonStyledButton>
        )
      }
    }

    payButtons.splice(payButtonsCols - 1, 0,
      this.createPaymentType(
        '$APPLY_DISCOUNTS',
        'fas fa-percent fa-2x',
        this.applyDiscounts,
        null,
        !staticConfig.discountsEnabled || orderHasPayment
      )
    )

    payButtons[(payButtonsCols * payButtonsRows) - 1] = this.createPaymentType(
      '$CLEAN_DISCOUNTS',
      'fas fa-times fa-2x',
      this.cleanDiscounts,
      null,
      !staticConfig.discountsEnabled || orderHasPayment
    )

    if (showOtherPayments) {
      payButtons[(payButtonsCols * payButtonsRows) - 2] = this.createPaymentType(
        '$OTHERS',
        'fas fa-ellipsis-h fa-2x',
        this.processOtherPayments,
        null,
        paymentButtonsDisabled
      )
    }

    return payButtons
  }

  removeFromOtherPayments(rootTenderTypes, i) {
    const indexToRemove = this.otherPaymentsOptions.indexOf(rootTenderTypes[i].id)
    if (indexToRemove > -1) {
      this.otherPaymentsOptions.splice(indexToRemove, 1)
    }
  }

  handlePaymentResponse(resultCode, message, payload) {
    const { selectedTable } = this.props

    if (resultCode === '0') {
      if (selectedTable != null) {
        this.props.msgBus.syncAction(
          'do_table_tender',
          this.selectedPaymentType,
          this.currentValue,
          null,
          null,
          payload,
          this.mobileDeviceType)
      } else {
        this.props.msgBus.syncAction(
          'doTender',
          this.currentValue,
          this.selectedPaymentType,
          false,
          false,
          false,
          this.mobileDeviceType,
          payload)
      }
    }
  }

  createPaymentType(text, icon, executeAction, onActionFinish, disabled, onClick) {
    const className = `test_OrderTender_${text.replace(/\s/g, '').replace('$', '').toUpperCase()}`
    return (
      <CommonStyledButton
        key="text"
        className={className}
        onClick={onClick}
        executeAction={executeAction}
        disabled={disabled}
        border={true}
      >
        {icon !== '' && <IconStyle className={icon} aria-hidden="true" disabled={disabled}/>}
        {icon !== '' && <br/>}
        <I18N id={text}>
          {(txt) => (<div>{txt}</div>)}
        </I18N>
      </CommonStyledButton>
    )
  }

  handleInputChange = (value) => {
    this.setState({ value: value })
    this.props.setNumPadValue('0')
  }

  cashPayment(tenderId) {
    const value = this.currentValue
    const { selectedTable } = this.props
    let action = ['do_table_tender', tenderId, value, null, null, null, this.mobileDeviceType]
    if (selectedTable == null) {
      action = ['doTender', value, tenderId, false, true, false, this.mobileDeviceType]
    } else if (this.props.selectedSeats && this.props.selectedSeats.length > 0) {
      action.push(null)
      action.push(this.props.selectedSeats)
    }

    return action
  }

  tefPayment(tenderType) {
    const value = this.currentValue

    if (window.mwapi != null) {
      if (this.mobileDeviceType == null) {
        this.props.showDialog({
          title: '$WARNING',
          type: DialogType.Alert,
          message: '$DEVICE_NOT_INITIALIZED'
        })
        return
      }

      this.selectedPaymentType = tenderType

      let lastTime = -1
      let lastTotaledState = null
      ensureArray(this.props.order.StateHistory.State).forEach(state => {
        if (state['@attributes'].state === 'TOTALED') {
          const time = Date.parse(state['@attributes'].timestamp)
          if (time > lastTime) {
            lastTime = time
            lastTotaledState = state
          }
        }
      })

      if (lastTotaledState == null) {
        return
      }

      const totaledDate = lastTotaledState['@attributes'].timestamp
        .replace(new RegExp('-', 'g'), '')
        .replace(new RegExp(':', 'g'), '')

      const requestData = {
        'transactionIdentifier': this.props.posId + this.props.order['@attributes'].orderId,
        'fiscalDate': totaledDate.substring(0, 8),
        'fiscalHour': totaledDate.substring(9, 15),
        'operator': this.props.operator.id
      }

      if (value > parseFloat(this.props.order['@attributes'].dueAmount)) {
        this.props.showDialog({
          title: '$WARNING',
          type: DialogType.Alert,
          message: '$NO_CHANGE_ALLOWED'
        })
        return
      }

      window.mwapi.processPayment('processPaymentCallback', value, tenderType, JSON.stringify(requestData), '0')
      return
    }

    const { selectedTable } = this.props
    let action = ['do_table_tender', tenderType, value]
    if (selectedTable == null) {
      action = ['doTender', value, tenderType, false, true]
    }

    this.props.msgBus.syncAction(...action)
  }

  externalPayment(tenderId) {
    const { selectedTable, selectedSeats } = this.props
    const value = this.currentValue
    const currentSelectedSeats = selectedSeats && selectedSeats.length === 0 ? null : selectedSeats

    let action = ['do_table_tender', tenderId, value, null, null, currentSelectedSeats, this.mobileDeviceType]
    if (selectedTable == null) {
      action = ['doTender', value, tenderId, false, true, false, this.mobileDeviceType]
    }
    return action
  }

  applyDiscounts() {
    const { selectedTable } = this.props
    if (selectedTable != null) {
      return ['do_apply_discounts', this.props.selectedTable.id]
    }
    return ['doApplicableCoupons']
  }

  cleanDiscounts() {
    const { selectedTable } = this.props
    if (selectedTable != null) {
      return ['do_clean_discounts', this.props.selectedTable.id]
    }
    return ['clean_discounts']
  }

  isElectronicTender = (tenderType) => {
    return tenderType === TenderType.CreditCard || tenderType === TenderType.DebitCard
  }

  shouldClearText = () => {
    const clear = this.state.clearCurrentText
    if (clear) {
      this.setState({ clearCurrentText: false })
    }
    return clear
  }

  processOtherPayments() {
    const { msgBus, selectedTable, selectedSeats } = this.props
    const value = this.currentValue
    const currentSelectedSeats = selectedSeats && selectedSeats.length === 0 ? null : selectedSeats

    msgBus.syncAction(
      'process_external_payments',
      this.otherPaymentsOptions,
      value,
      selectedTable != null,
      currentSelectedSeats,
      this.mobileDeviceType)
  }
}

MobileDesktopTendersRenderer.propTypes = {
  order: OrderPropTypes,
  msgBus: PropTypes.shape({
    syncAction: PropTypes.func.isRequired
  }).isRequired,
  selectedTable: TablePropTypes,
  staticConfig: StaticConfigPropTypes,
  selectedSeats: PropTypes.arrayOf(PropTypes.number),
  showDialog: PropTypes.func,
  id: PropTypes.string,
  showTef: PropTypes.bool,
  workingMode: PropTypes.object,
  selectedTenderDivisionValue: PropTypes.string,
  setNumPadValue: PropTypes.func,
  deviceType: PropTypes.number,
  operator: OperatorPropTypes,
  posId: PropTypes.number,
  actionEnd: PropTypes.func,
  saleType: PropTypes.string,
  actionRequest: PropTypes.func
}
