import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'
import { ensureArray, ensureDecimals } from '3s-posui/utils'

import { TotemButton, TotemButtonGrid, TotemTenderText } from './StyledOrderTenders'

import OrderPropTypes from '../../../../prop-types/OrderPropTypes'
import TablePropTypes from '../../../../prop-types/TablePropTypes'
import OperatorPropTypes from '../../../../prop-types/OperatorPropTypes'
import DialogType from '../../../../constants/DialogType'
import StaticConfigPropTypes from '../../../../prop-types/StaticConfigPropTypes'
import { isTefPaymentType } from './OrderTendersUtil'

function getRootTenderTypes(tenderTypes, saleType, showTef = true) {
  return tenderTypes.filter(function (tenderType) {
    if (tenderType.parentId != null) {
      return false
    } else if (isTefPaymentType(tenderType) && showTef) {
      return true
    } else if (!isTefPaymentType(tenderType) && (tenderType.showInFC)) {
      return true
    }
    return false
  })
}

export default class TotemTendersRenderer extends Component {
  constructor(props) {
    super(props)

    const dueAmount = this.props.order['@attributes'].dueAmount
    const valueToPay = ensureDecimals(Number(dueAmount || '0'))
    this.state = {
      valueToPay,
      value: valueToPay,
      dueAmount
    }
    this.currentValue = this.state.valueToPay
    this.selectedPaymentType = null

    this.handlePaymentResponse = this.handlePaymentResponse.bind(this)
  }

  static getDerivedStateFromProps(props, state) {
    const dueAmount = parseFloat(props.order['@attributes'].dueAmount)
    const dueAmountNext = dueAmount < 0 ? 0 : dueAmount.toString()
    const nextDue = ensureDecimals(Number(dueAmountNext || '0'))
    const nextState = {}

    if (nextDue !== state.valueToPay) {
      nextState.valueToPay = nextDue
      nextState.value = nextDue
    }
    nextState.dueamount = dueAmountNext

    return nextState
  }

  render() {
    const { value } = this.state
    const { selectedTenderDivisionValue, staticConfig } = this.props
    const { tenderTypes } = staticConfig

    this.currentValue = selectedTenderDivisionValue !== '0' ? selectedTenderDivisionValue : value
    const orderIsPaid = parseFloat(this.state.dueamount) === 0
    const paymentBtnsDisabled = orderIsPaid || this.currentValue === '0.00'
    const payButtonsCols = 1
    const payButtonsRows = 2
    const payButtons = this.createTotemPaymentButton(payButtonsCols, payButtonsRows, tenderTypes, paymentBtnsDisabled)

    return (
      <TotemButtonGrid>{payButtons}</TotemButtonGrid>

    )
  }

  createTotemPaymentButton(payButtonsCols, payButtonsRows, tenderTypes, paymentBtnsDisabled) {
    const saleType = (this.props.saleType || 'FC').toString()

    const rootTenderTypes = getRootTenderTypes(tenderTypes, saleType)
    const electronicTenderTypes = rootTenderTypes.filter(x => x.electronicType !== 'NON_ELECTRONIC')

    const payButtons = []

    payButtons.push(
      this.createPaymentType(
        '$CREDIT',
        null,
        null,
        paymentBtnsDisabled,
        () => this.tefPayment(electronicTenderTypes[0].id),
        'fas fa-credit-card',
        electronicTenderTypes[0].id
      )
    )

    payButtons.push(
      this.createPaymentType(
        '$DEBIT',
        null,
        null,
        paymentBtnsDisabled,
        () => this.tefPayment(electronicTenderTypes[1].id),
        'fas fa-credit-card',
        electronicTenderTypes[1].id
      )
    )

    return payButtons
  }

  handlePaymentResponse(resultCode, message, payload) {
    const { selectedTable, deviceType } = this.props

    if (resultCode === '0') {
      if (selectedTable != null) {
        this.props.msgBus.syncAction(
          'do_table_tender',
          this.selectedPaymentType,
          this.currentValue,
          null,
          null,
          payload,
          deviceType)
      } else {
        this.props.msgBus.syncAction(
          'doTender',
          this.currentValue,
          this.selectedPaymentType,
          false,
          false,
          false,
          deviceType,
          payload)
      }
    }
  }

  createPaymentType(text, executeAction, onActionFinish, disabled, onClick, icon = null, key = null) {
    return (
      <TotemButton
        className={`test_TotemTendersRenderer_${text.replace('$', '')}`}
        onClick={onClick}
        executeAction={executeAction}
        disabled={disabled}
        key={key}
      >
        <I18N id={text}>
          {(txt) => (<TotemTenderText>{txt}</TotemTenderText>)}
        </I18N>
        {icon && <i className={icon}/>}
      </TotemButton>
    )
  }

  tefPayment(tenderType) {
    const value = this.currentValue
    const { deviceType } = this.props

    if (window.mwapi != null) {
      if (deviceType == null) {
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
      ensureArray(this.props.order.StateHistory.State)
        .forEach(state => {
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

      window.mwapi.processPayment('processPaymentCallBack', value, tenderType, JSON.stringify(requestData), '0')
      return
    }

    const { selectedTable } = this.props
    let action = ['do_table_tender', tenderType, value]
    if (selectedTable == null) {
      action = ['doTender', value, tenderType, false, true]
    }

    this.props.msgBus.syncAction(...action)
  }
}

TotemTendersRenderer.propTypes = {
  order: OrderPropTypes,
  msgBus: PropTypes.shape({
    syncAction: PropTypes.func.isRequired
  }).isRequired,
  selectedTable: TablePropTypes,
  staticConfig: StaticConfigPropTypes,
  showDialog: PropTypes.func,
  id: PropTypes.string,
  selectedTenderDivisionValue: PropTypes.string,
  deviceType: PropTypes.number,
  operator: OperatorPropTypes,
  posId: PropTypes.number,
  saleType: PropTypes.string
}
