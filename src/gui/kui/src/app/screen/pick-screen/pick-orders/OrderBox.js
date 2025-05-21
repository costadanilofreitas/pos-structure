import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { bindActionCreators } from 'redux'
import isEmpty from 'lodash/isEmpty'

import { OrderInfo, OrderInfoBox } from './StyledPickOrders'
import { sendBumpBarCommandAction } from '../../../../actions'
import withState from '../../../../util/withState'
import parseMacros from '../../../../util/CellFormater'

class OrderBox extends Component {
  constructor(props) {
    super(props)

    this.autoCommandTimer = null
  }

  render() {
    const { theme, order, blink, fontSize, maxWidth, withImage } = this.props
    if (isEmpty(order)) {
      return <OrderInfoBox withImage={withImage}/>
    }
    this.setAutoCommandTimeout(order)

    const name = this.getName(order)
    const orderId = this.getId(order)
    const currentOrderId = orderId.slice(-3)
    return (
      <OrderInfoBox
        theme={theme}
        flexGrow={1}
        className={`test_ReadyOrdersBox_${0}`}
        withImage={withImage}
      >
        {this.getOrderBoxContent(name, currentOrderId, blink, fontSize, maxWidth)}
      </OrderInfoBox>
    )
  }

  componentWillUnmount() {
    this.removeAutoCommandTimer()
  }

  autoCommandHandler = () => {
    const { executeBumpCommand, order } = this.props

    if (order == null) {
      return
    }

    const { command } = this.getAutoOrderCommand()
    executeBumpCommand(command, order.attrs.order_id)
    this.autoCommandTimer = null
  }

  setAutoCommandTimeout(order) {
    this.removeAutoCommandTimer()
    const time = this.getAutoCommandTime(order)
    if (isNaN(time)) {
      return
    }

    this.autoCommandTimer = setTimeout(this.autoCommandHandler, time * 1000)
  }

  getAutoOrderCommand() {
    const { autoOrderCommand } = this.props
    if (!autoOrderCommand) {
      return { time: 0, command: '' }
    }
    return autoOrderCommand
  }

  removeAutoCommandTimer() {
    if (this.autoCommandTimer) {
      clearTimeout(this.autoCommandTimer)
      this.autoCommandTimer = null
    }
  }

  getAutoCommandTime(order) {
    const { time: commandTime } = this.getAutoOrderCommand()
    const currentOrderTime = this.getOrderTimeOnExpo(order)
    return Math.max(commandTime - currentOrderTime, 0)
  }

  getOrderTimeOnExpo(order) {
    const { timeDelta } = this.props
    let orderTime = order.attrs.display_time_gmt
    if (!orderTime) {
      orderTime = order.attrs.display_time
    }
    return (new Date() - new Date(new Date(orderTime).getTime() + timeDelta)) / 1000
  }

  getName(order) {
    if (order.props && order.props.CUSTOMER_NAME) {
      return order.props.CUSTOMER_NAME.toString().toUpperCase()
    }

    return null
  }

  getId(order) {
    if (order && order.attrs) {
      return order.attrs.order_id
    }

    return ''
  }

  getOrderBoxContent(name, orderId, blink, fontSize, maxWidth) {
    const { format, order, timeDelta } = this.props

    return (
      <OrderInfo blink={blink} fontSize={fontSize} maxWidth={maxWidth} className={`test_OrdersBox_${orderId}`}>
        {parseMacros(format, order, timeDelta)}
      </OrderInfo>
    )
  }

  generateKeyFromOrder(order, orderId, index) {
    return `${orderId}_${this.lastUpdate(order)}_${index}_ready`
  }

  lastUpdate(order) {
    return order && order.attrs && order.attrs.prod_state_last_update && new Date(order.attrs.prod_state_last_update)
  }
}

OrderBox.propTypes = {
  order: PropTypes.object,
  theme: PropTypes.object,
  blink: PropTypes.bool,
  fontSize: PropTypes.number,
  executeBumpCommand: PropTypes.func,
  timeDelta: PropTypes.number,
  autoOrderCommand: PropTypes.object,
  format: PropTypes.string,
  maxWidth: PropTypes.string,
  withImage: PropTypes.bool
}

OrderBox.defaultProps = {
  maxWidth: '15%'
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators({
    executeBumpCommand: (command, orderId) => sendBumpBarCommandAction({ command, orderId })
  }, dispatch)
}

export default withState(OrderBox, mapDispatchToProps, 'timeDelta')
