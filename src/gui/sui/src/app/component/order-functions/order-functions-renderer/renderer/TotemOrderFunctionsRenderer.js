import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'

import ActionButton from '../../../../../component/action-button'
import MessageBusPropTypes from '../../../../../prop-types/MessageBusPropTypes'
import { TotemActionButtonsContainer } from '../StyledTotemOrderFunctionsRenderer'
import { checkOrderItems } from '../common/TotaledOrderRenderer'
import ScreenOrientation from '../../../../../constants/ScreenOrientation'

class TotemOrderFunctionsRenderer extends Component {
  constructor(props) {
    super(props)
    this.handleCleanOrder = this.handleCleanOrder.bind(this)
  }

  render() {
    const { order, screenOrientation } = this.props
    const validOrder = order != null && parseFloat(order.totalAmount) > 0 && order.state === 'IN_PROGRESS'
    const buttonsDirection = screenOrientation === ScreenOrientation.Portrait ? 'column' : 'row'

    return (
      <TotemActionButtonsContainer style={{ flexDirection: `${buttonsDirection}` }}>
        <ActionButton
          className={'test_SaleSummary_CANCEL'}
          disabled={false}
          onClick={() => this.voidKioskOrder()}
        >
          <i className="fa fa-times fa" aria-hidden="true" style={{ margin: '0.5vh' }}/><br/>
          <I18N id="$CLEAR_ORDER"/>
        </ActionButton>
        <ActionButton
          className={'test_SaleSummary_CLEAN'}
          disabled={!checkOrderItems(order)}
          onClick={this.handleCleanOrder}
        >
          <i className="far fa-trash-alt" aria-hidden="true" style={{ margin: '0.5vh' }}/><br/>
          <I18N id="$CLEAN_ORDERS"/>
        </ActionButton>
        <ActionButton
          className={'test_OrderFunctions_TOTAL-ORDER'}
          disabled={!validOrder}
          onClick={this.props.onTotal}
        >
          <i className="fas fa-dollar-sign" aria-hidden="true" style={{ margin: '0.5vh' }}/><br/>
          <I18N id="$PAY"/>
        </ActionButton>
      </TotemActionButtonsContainer>
    )
  }

  handleCleanOrder() {
    const { order } = this.props
    this.deleteLines(this.getAllLineNumbers(order))
    this.props.onCleanOrder()
  }

  getAllLineNumbers(order) {
    const linesWithQuantity = order.SaleLine.filter(x => x.level === '0' && parseInt(x.qty, 10) > 0)
    return linesWithQuantity.map(function (item) {
      return item.lineNumber
    })
  }

  deleteLines(linesNumber) {
    this.props.msgBus.syncAction('do_void_lines', linesNumber.join('|'))
  }

  voidKioskOrder = () => {
    this.props.msgBus.syncAction('do_void_kiosk_order')
  }
}

TotemOrderFunctionsRenderer.propTypes = {
  order: PropTypes.object,
  msgBus: MessageBusPropTypes,
  onTotal: PropTypes.func,
  onCleanOrder: PropTypes.func,
  screenOrientation: PropTypes.number
}

TotemOrderFunctionsRenderer.defaultProps = {
  selectedLine: {}
}

export default TotemOrderFunctionsRenderer
