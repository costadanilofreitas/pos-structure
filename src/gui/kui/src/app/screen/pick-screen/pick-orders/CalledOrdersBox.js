import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { Container } from './StyledPickOrders'
import OrderBox from './OrderBox'

class CalledOrdersBox extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    const { orders, flex, autoOrderCommand, format, withImage } = this.props
    const nextOrders = this.getNextOrders(orders)

    return (
      <Container flex={flex} height={'100%'} width={'20%'}>
        <Container flex={2} />
        <Container flex={11}>
          {
            nextOrders.map((order, index) => (
              <OrderBox
                key={(order && order.attrs) ? order.attrs.order_id : index}
                order={order}
                fontSize={4}
                maxWidth={'20%'}
                autoOrderCommand={autoOrderCommand}
                format={format}
                withImage={withImage}
              />
            ))
          }
        </Container>
        <Container flex={1}/>
      </Container>
    )
  }

  getNextOrders(orders) {
    const nextOrders = orders.length > 8 ? orders.slice(0, 8) : orders.slice(0, orders.length)
    while (nextOrders.length < 8) {
      nextOrders.push({})
    }

    return nextOrders
  }
}

CalledOrdersBox.defaultProps = {
  orders: [],
  flex: 1
}

CalledOrdersBox.propTypes = {
  orders: PropTypes.array,
  flex: PropTypes.number,
  autoOrderCommand: PropTypes.object,
  format: PropTypes.string,
  withImage: PropTypes.bool
}

export default CalledOrdersBox
