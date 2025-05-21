import React, { Component } from 'react'
import PropTypes from 'prop-types'

import TableOrdersRenderer from './renderer'
import MessageBusPropTypes from '../../../prop-types/MessageBusPropTypes'
import WorkingModePropTypes from '../../../prop-types/WorkingModePropTypes'
import TablePropTypes from '../../../prop-types/TablePropTypes'


export default class TableOrders extends Component {
  constructor(props) {
    super(props)

    this.state = {
      currentTime: this.props.getCurrentDate()
    }

    this.handleOnOrderChange = this.handleOnOrderChange.bind(this)
    this.handleOnOrderCancel = this.handleOnOrderCancel.bind(this)
    this.handleOnOrderPrint = this.handleOnOrderPrint.bind(this)
  }

  render() {
    const { orders, status, workingMode } = this.props
    return (
      <TableOrdersRenderer
        orders={orders}
        status={status}
        currentTime={this.state.currentTime}
        onOrderChange={this.handleOnOrderChange}
        onOrderCancel={this.handleOnOrderCancel}
        onOrderPrint={this.handleOnOrderPrint}
        workingMode={workingMode}
      />
    )
  }

  componentDidMount() {
    this.interval = setInterval(() => this.setState({ currentTime: this.props.getCurrentDate() }), 1000)
  }

  componentWillUnmount() {
    clearInterval(this.interval)
  }

  handleOnOrderChange(order) {
    this.props.msgBus.syncAction('edit_table_order', order.orderId)
  }

  handleOnOrderCancel(order) {
    this.props.msgBus.syncAction('cancel_table_order', order.orderId, this.props.table.id)
  }

  handleOnOrderPrint(order) {
    this.props.msgBus.syncAction('print_table_order', order.orderId)
  }
}

TableOrders.propTypes = {
  orders: PropTypes.array,
  status: PropTypes.number.isRequired,
  table: TablePropTypes,
  workingMode: WorkingModePropTypes,
  getCurrentDate: PropTypes.func.isRequired,
  msgBus: MessageBusPropTypes.isRequired
}
