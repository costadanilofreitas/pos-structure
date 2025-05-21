import React, { Component } from 'react'
import PropTypes from 'prop-types'

import OrderFunctionsRenderer from './order-functions-renderer'
import OrderPropTypes from '../../../prop-types/OrderPropTypes'
import MessageBusPropTypes from '../../../prop-types/MessageBusPropTypes'
import WorkingModePropTypes from '../../../prop-types/WorkingModePropTypes'
import { ensureArray } from '../../../util/renderUtil'
import { findSelectedLine, findSelectedParent, getOpenOption } from '../../util/saleLineUtil'
import TablePropTypes from '../../../prop-types/TablePropTypes'
import StaticConfigPropTypes from '../../../prop-types/StaticConfigPropTypes'
import { isDeliveryOrder, isLocalDelivery } from '../../../util/orderUtil'


export default class OrderFunctions extends Component {
  constructor(props) {
    super(props)

    this.handleOnStartOrder = this.handleOnStartOrder.bind(this)
    this.handleOnVoidSale = this.handleOnVoidSale.bind(this)
    this.handleOnVoidLastLine = this.handleOnVoidLastLine.bind(this)
    this.handleOnTotal = this.handleOnTotal.bind(this)
    this.handleOnProduce = this.handleOnProduce.bind(this)
    this.handleOnSeatIncrement = this.handleOnSeatIncrement.bind(this)
    this.handleOnSendOrder = this.handleOnSendOrder.bind(this)
    this.handleOnDeleteLine = this.handleOnDeleteLine.bind(this)
    this.handleOnPriceOverwrite = this.handleOnPriceOverwrite.bind(this)
    this.handleOnComment = this.handleOnComment.bind(this)
    this.handleOnSeatChange = this.handleOnSeatChange.bind(this)
    this.handleOnModify = this.handleOnModify.bind(this)
    this.handleOnHold = this.handleOnHold.bind(this)
    this.handleOnFire = this.handleOnFire.bind(this)
    this.handleOnHighPriority = this.handleOnHighPriority.bind(this)
    this.handleOnDontMake = this.handleOnDontMake.bind(this)
    this.onChangeProductionCourse = this.onChangeProductionCourse.bind(this)
    this.handleCleanItemTags = this.handleCleanItemTags.bind(this)
    this.getCurrentSaleLine = this.getCurrentSaleLine.bind(this)
    this.deliveryEnabled = this.deliveryEnabled.bind(this)
    this.isChangingOrder = this.isChangingOrder.bind(this)
    this.hasModifier = this.hasModifier.bind(this)
  }

  render() {
    const modifyEnabled = this.hasModifiers(this.props.selectedLine)

    return (
      <OrderFunctionsRenderer
        {...this.props}
        themes={this.props.theme}
        onStartOrder={this.handleOnStartOrder}
        onVoidOrder={this.handleOnVoidSale}
        onVoidLast={this.handleOnVoidLastLine}
        onTotal={this.handleOnTotal}
        onProduce={this.handleOnProduce}
        onSeatIncrement={this.handleOnSeatIncrement}
        onSeatChange={this.handleOnSeatChange}
        onSendOrder={this.handleOnSendOrder}
        onDeleteLine={this.handleOnDeleteLine}
        onPriceOverwrite={this.handleOnPriceOverwrite}
        onComment={this.handleOnComment}
        onChangeSeat={this.handleOnSeatChange}
        onModify={this.handleOnModify}
        onHold={this.handleOnHold}
        onFire={this.handleOnFire}
        onDontMake={this.handleOnDontMake}
        onHighPriority={this.handleOnHighPriority}
        onChangeProductionCourse={this.onChangeProductionCourse}
        onCleanItemTags={this.handleCleanItemTags}
        onAskBarcode={this.props.onAskBarcode}
        workingMode={this.props.workingMode}
        modifyEnabled={modifyEnabled}
        selectedTable={this.props.selectedTable}
        deliveryEnabled={this.deliveryEnabled}
        isChangingOrder={this.isChangingOrder}
        hasModifier={this.hasModifier}
      />
    )
  }

  handleOnVoidSale() {
    const actionName = this.props.selectedTable != null ? 'cancel_current_table_order' : 'do_void_order'
    this.props.msgBus.syncAction(actionName).then(response => {
      if (response.ok && response.data === 'True') {
        this.props.onUnselectLine()
      }
    })
  }

  handleOnStartOrder() {
    this.props.msgBus.syncAction('doStartOrder', this.props.saleType)
  }

  handleOnVoidLastLine() {
    let lastSaleLine = null
    ensureArray(this.props.order.SaleLine).forEach(saleLine => {
      if (OrderFunctions.hasHigherLineNumber(lastSaleLine, saleLine) &&
          parseInt(saleLine['@attributes'].qty, 10) > 0 &&
          saleLine['@attributes'].level === '0') {
        lastSaleLine = saleLine
      }
    })

    if (lastSaleLine == null) {
      return
    }

    this.props.msgBus.syncAction('do_void_lines', lastSaleLine['@attributes'].lineNumber)
  }

  handleOnTotal() {
    const { order, staticConfig } = this.props
    let total = false

    if (isLocalDelivery(order) && staticConfig.deliveryAddress) {
      this.props.msgBus.syncAction('delivery_address').then(response => {
        if (response.ok && response.data !== 0 && response.data.toLowerCase() !== 'false') {
          total = true
        }
      }).finally(() => {
        if (total) {
          this.callDoTotal()
        }
      })
    } else {
      this.callDoTotal()
    }
  }

  callDoTotal() {
    this.props.msgBus.syncAction('doTotal').then(totalResponse => {
      if (totalResponse.ok && totalResponse.data != null) {
        if (totalResponse.data !== 'True') {
          this.findOptionAndSetLine()
        }
      }
    })
  }

  handleOnProduce() {
    this.props.msgBus.syncAction('produce_delivery_order', this.props.order.orderId, true, true)
  }

  handleOnSeatIncrement() {
    let currentSeat = this.props.selectedSeat || 0
    currentSeat++
    const maxSeats = parseInt(this.props.selectedTable.serviceSeats, 10)
    if (currentSeat > maxSeats) {
      currentSeat = 0
    }
    if (this.props.onSeatChange) {
      this.props.onSeatChange(currentSeat)
    }
  }

  handleOnSendOrder(logout) {
    const { selectedTable, msgBus, changeMenu } = this.props
    let promise

    if (selectedTable != null) {
      const tabId = selectedTable.tabNumber != null ? selectedTable.tabNumber : undefined
      promise = msgBus.syncAction('store_table_order', selectedTable.id, tabId)
    } else {
      promise = msgBus.syncAction('doStoreOrder')
    }

    promise.then(response => {
      if (response.ok && response.data != null) {
        if (response.data === 'True') {
          if (selectedTable != null) {
            if (logout === true) {
              msgBus.parallelSyncAction('pause_user')
              changeMenu(null)
            }
          }
        } else {
          this.findOptionAndSetLine()
        }
      }
    })
  }

  findOptionAndSetLine() {
    const { order, onLineClick } = this.props
    const selectedLine = getOpenOption(order.SaleLine)
    if (selectedLine != null) {
      const selectedParent = findSelectedParent(order, selectedLine)
      onLineClick(selectedLine, selectedParent, true, true)
    }
  }

  handleOnDeleteLine() {
    const selectedLine = this.getCurrentSaleLine(this.props.selectedLine, true)
    this.props.msgBus.syncAction('do_void_lines', selectedLine.lineNumber).then(response => {
      if (response.ok && response.data.toLowerCase() === 'true') {
        this.props.onUnselectLine()
      }
    })
  }

  handleOnPriceOverwrite() {
    const selectedLine = this.getCurrentSaleLine(this.props.selectedLine, true)
    const { lineNumber, itemPrice, itemId, level, partCode } = selectedLine || {}
    this.props.msgBus.syncAction(
      'doOverwritePrice',
      lineNumber,
      itemPrice,
      itemId,
      level,
      partCode,
      this.deliveryEnabled())
  }

  handleOnComment() {
    const selectedLine = this.getCurrentSaleLine(this.props.selectedLine, true)
    if (!selectedLine || selectedLine.itemType === 'OPTION') {
      this.props.msgBus.syncAction('do_comment', null, null, null, null, null)
      return
    }

    const { lineNumber, level, itemId, partCode } = selectedLine
    this.props.msgBus.syncAction('do_comment', lineNumber, level, itemId, partCode, this.getCommentId(selectedLine))
  }

  handleOnSeatChange() {
    const selectedLine = this.getCurrentSaleLine(this.props.selectedLine, true)
    if (selectedLine == null) {
      return
    }
    const saleLineParams = {
      lineNumber: selectedLine.lineNumber,
      itemId: selectedLine.itemId,
      level: selectedLine.level,
      partCode: selectedLine.partCode
    }
    this.props.msgBus.syncAction('choose_line_seat', JSON.stringify(saleLineParams))
  }

  handleOnModify() {
    if (this.hasModifiers(this.props.selectedLine)) {
      this.props.onToggleSalePanel()
      this.props.onShowModifierScreen()
    }
  }

  handleOnHold() {
    const selectedLine = this.getCurrentSaleLine(this.props.selectedLine, true)
    if (selectedLine == null) {
      return
    }

    this.props.msgBus.syncAction('do_hold_item', JSON.stringify(selectedLine))
  }

  handleOnFire() {
    const selectedLine = this.getCurrentSaleLine(this.props.selectedLine, true)
    if (selectedLine == null) {
      return
    }

    this.props.msgBus.syncAction('do_fire_item', JSON.stringify(selectedLine))
  }

  handleOnHighPriority() {
    const selectedLine = this.getCurrentSaleLine(this.props.selectedLine, true)
    if (selectedLine == null) {
      return
    }

    this.props.msgBus.syncAction('do_high_priority_item', JSON.stringify(selectedLine))
  }

  handleOnDontMake() {
    const selectedLine = this.getCurrentSaleLine(this.props.selectedLine, true)
    if (selectedLine == null) {
      return
    }

    this.props.msgBus.syncAction('dont_make_item', JSON.stringify(selectedLine))
  }

  onChangeProductionCourse() {
    const selectedLine = this.getCurrentSaleLine(this.props.selectedLine, true)
    if (selectedLine == null) {
      return
    }

    this.props.msgBus.syncAction('change_production_course_item', JSON.stringify(selectedLine))
  }

  handleCleanItemTags() {
    const selectedLine = this.getCurrentSaleLine(this.props.selectedLine, true)
    if (selectedLine == null) {
      return
    }

    const commentLine = this.getCommentId(this.props.selectedLine)
    this.props.msgBus.syncAction('do_clean_item_tags', JSON.stringify(selectedLine), commentLine)
  }

  static hasHigherLineNumber(currentSaleLine, newSaleLine) {
    if (currentSaleLine == null) {
      return true
    }
    return parseInt(newSaleLine['@attributes'].lineNumber, 10) > parseInt(currentSaleLine['@attributes'].lineNumber, 10)
  }

  getCommentId(selectedLine) {
    const { order } = this.props
    let commentId = '-1'

    for (let i = 0; i < order.SaleLine.length; i++) {
      const saleLineAttributes = order.SaleLine[i]['@attributes']
      if (saleLineAttributes.itemId === selectedLine.itemId &&
          saleLineAttributes.level === selectedLine.level &&
          saleLineAttributes.lineNumber === selectedLine.lineNumber &&
          saleLineAttributes.partCode === selectedLine.partCode) {
        if (order.SaleLine[i].Comment.length > 0) {
          commentId = order.SaleLine[i].Comment[0]['@attributes'].commentId
        }
      }
    }

    return commentId
  }

  getCurrentSaleLine(saleLine, root) {
    if (saleLine == null) {
      return null
    }

    const { order } = this.props
    return root ? findSelectedParent(order, saleLine) : findSelectedLine(order, saleLine)
  }

  hasModifiers(selectedLine) {
    let modifyEnabled = false
    if (selectedLine != null) {
      const rootSaleLine = findSelectedParent(this.props.order, selectedLine)
      if (rootSaleLine != null) {
        modifyEnabled = this.props.modifiers.modifiers[parseInt(rootSaleLine['@attributes'].partCode, 10)] != null
      }
    }
    return modifyEnabled
  }

  deliveryEnabled() {
    const { availableSaleTypes } = this.props.staticConfig
    const defaultSaleType = availableSaleTypes != null ? availableSaleTypes[0] : null
    return (this.props.saleType === 'DELIVERY' || defaultSaleType === 'DELIVERY')
  }

  isChangingOrder(order) {
    if (isDeliveryOrder(order.CustomOrderProperties)) {
      return false
    }

    if (!this.orderHasStateHistory(order)) {
      return false
    }

    return this.orderWasStored(order) && !this.orderIsInProgress(order)
  }

  orderHasStateHistory(order) {
    if (order.StateHistory == null) {
      return false
    }

    return Array.isArray(order.StateHistory.State) && order.StateHistory.State.length > 0
  }

  orderWasStored(order) {
    return order.StateHistory.State.some(elem => elem['@attributes'].state === 'STORED')
  }

  orderIsInProgress(order) {
    const lastStateHistoryLength = order.StateHistory.State.length - 1
    return order.StateHistory.State[lastStateHistoryLength] === 'IN_PROGRESS'
  }

  hasModifier(selectedParent) {
    const saleLines = this.props.order.SaleLine
    if (selectedParent == null || saleLines.length === 0) {
      return false
    }

    if (this.parentHasModifier(selectedParent)) {
      return true
    }

    return this.someChildHasModifier(selectedParent, saleLines)
  }

  partCodeHasModifier(partCode) {
    return this.props.modifiers.modifiers[partCode] != null
  }

  parentHasModifier(selectedParent) {
    return this.partCodeHasModifier(selectedParent.partCode)
  }

  someChildHasModifier(selectedParent, saleLines) {
    const childItemId = `${selectedParent.itemId}.${selectedParent.partCode}`
    const selectParentChild = saleLines.filter(x => x.itemId.startsWith(childItemId))
    for (let i = 0; i < selectParentChild.length; i++) {
      if (this.partCodeHasModifier(selectParentChild[i].partCode)) {
        return true
      }
    }

    return false
  }
}

OrderFunctions.propTypes = {
  /* Common props */
  order: OrderPropTypes,
  onUnselectLine: PropTypes.func,
  selectedLine: PropTypes.object,
  saleType: PropTypes.string,
  changeMenu: PropTypes.func,
  selectedTable: TablePropTypes,
  staticConfig: StaticConfigPropTypes,

  /* Mobile props */
  msgBus: MessageBusPropTypes,

  /* Desktop props */
  selectedSeat: PropTypes.number,
  onSeatChange: PropTypes.func,
  skipAutoSelect: PropTypes.bool,
  modifierScreenOpen: PropTypes.bool,
  onShowModifierScreen: PropTypes.func,
  onLineClick: PropTypes.func,
  onToggleSalePanel: PropTypes.func,
  workingMode: WorkingModePropTypes,
  voidOrClearOption: PropTypes.func,
  onAskBarcode: PropTypes.func,
  modifiers: PropTypes.object,
  theme: PropTypes.object,

  /* Totem Props */
  onCleanOrder: PropTypes.func
}
