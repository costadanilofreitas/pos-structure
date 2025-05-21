import React, { Component } from 'react'
import PropTypes from 'prop-types'

import TableOrderDetails from './table-order-details'

export default class MobileTableOrdersRenderer extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    const { orders, classes } = this.props

    return (
      <div className={classes.rootContainer}>
        {orders.map((order, index) => (
          <TableOrderDetails
            key={`tod${index}`}
            order={order}
            currentTime={this.props.currentTime}
            onOrderChange={this.props.onOrderChange}
            onOrderCancel={this.props.onOrderCancel}
            onOrderPrint={this.props.onOrderPrint}
            tableStatus={this.props.status}
          />))}
      </div>
    )
  }
}

MobileTableOrdersRenderer.propTypes = {
  orders: PropTypes.array,
  status: PropTypes.number.isRequired,
  currentTime: PropTypes.object,
  onOrderChange: PropTypes.func,
  onOrderCancel: PropTypes.func,
  onOrderPrint: PropTypes.func,
  classes: PropTypes.object
}
