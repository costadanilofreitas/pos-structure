import React, { Component } from 'react'
import PropTypes from 'prop-types'

import OrderTotalRenderer from './order-total-renderer'
import { orderNotInState } from '../../util/orderValidator'
import OrderState from '../../model/OrderState'
import OrderPropTypes from '../../../prop-types/OrderPropTypes'
import TablePropTypes from '../../../prop-types/TablePropTypes'
import WorkingModePropTypes from '../../../prop-types/WorkingModePropTypes'
import { lastGroupSaleLine } from '../../../util/orderUtil'


export default class OrderTotal extends Component {
  render() {
    return (
      <OrderTotalRenderer
        order={this.props.order}
        skipAutoSelect={this.props.skipAutoSelect}
        customerName={this.props.customerName}
        workingMode={this.props.workingMode}
        totalOrder={this.orderTotal()}
        orderId={this.orderId()}
        saleLine={this.saleLine()}
        isSalePanelVisible={this.props.isSalePanelVisible}
        onLineClick={this.props.onLineClick}
        selectedLine={this.props.selectedLine}
        selectedParent={this.props.selectedParent}
        selectedTable={this.props.selectedTable}
        onToggleSalePanel={this.props.onToggleSalePanel}
      />
    )
  }

  orderId() {
    const { order } = this.props
    if (orderNotInState(order, OrderState.InProgress, OrderState.Totaled)) {
      return -1
    }
    return this.props.order['@attributes'].orderId
  }

  orderTotal() {
    const { order } = this.props
    if (orderNotInState(order, OrderState.InProgress, OrderState.Totaled)) {
      return -1
    }
    return parseFloat(this.props.order['@attributes'].totalGross)
  }

  saleLine() {
    const { order } = this.props
    if (orderNotInState(order, OrderState.InProgress, OrderState.Totaled)) {
      return -1
    }
    return this.formatObjectSaleLine(order)
  }

  formatObjectSaleLine(order) {
    const saleLineObject = {
      qty: '',
      productName: '',
      total: ''
    }

    let total = 0
    const groupedSaleLine = lastGroupSaleLine(order) || []

    groupedSaleLine.forEach(x => {
      if (x && x['@attributes'].multipliedQty && x['@attributes'].unitPrice) {
        total += (x['@attributes'].multipliedQty * x['@attributes'].unitPrice)
        if (x['@attributes'].itemDiscount != null) {
          total -= x['@attributes'].itemDiscount
        }
      }
    })

    if (groupedSaleLine[0] && groupedSaleLine[0]['@attributes'].multipliedQty > 0) {
      saleLineObject.qty = groupedSaleLine[0]['@attributes'].multipliedQty
      saleLineObject.productName = groupedSaleLine[0]['@attributes'].productName
      saleLineObject.total = total
    }
    return saleLineObject
  }
}

OrderTotal.propTypes = {
  order: OrderPropTypes,
  onToggleSalePanel: PropTypes.func,
  isSalePanelVisible: PropTypes.bool,
  selectedTable: TablePropTypes,
  selectedLine: PropTypes.object,
  selectedParent: PropTypes.object,
  onLineClick: PropTypes.func,
  skipAutoSelect: PropTypes.bool,
  customerName: PropTypes.string,
  workingMode: WorkingModePropTypes
}
