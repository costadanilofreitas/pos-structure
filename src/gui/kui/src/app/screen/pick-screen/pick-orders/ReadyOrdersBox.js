import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Container } from './StyledPickOrders'
import OrderBox from './OrderBox'

class ReadyOrdersBox extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    const { orders, flex, autoOrderCommand, format, withImage } = this.props
    const firstOrder = orders.length > 0 ? orders[0] : null
    const nextOrders = this.getNextOrders(orders)

    return (
      <Container flex={flex} height={'100%'} width={'100%'}>
        <Container flex={3} />
        <Container
          flex={7}
          width={withImage ? 'unset' : '90%'}
          alignSelf={withImage ? 'none' : 'center'}
        >
          <OrderBox
            order={firstOrder}
            blink={true}
            maxWidth={'50%'}
            fontSize={10}
            format={format}
            withImage={withImage}
            autoOrderCommand={autoOrderCommand}
          />
        </Container>
        <Container
          flex={3}
          direction="row"
          width={withImage ? 'unset' : '90%'}
          alignSelf={withImage ? 'none' : 'center'}
        >
          {withImage &&
            <Container flex={0.5}/>
          }
          <Container flex={11} direction="row">
            {
              nextOrders.map((order, index) => (
                <OrderBox
                  key={(order && order.attrs) ? order.attrs.order_id : index}
                  order={order}
                  fontSize={5}
                  maxWidth={'15%'}
                  autoOrderCommand={autoOrderCommand}
                  format={format}
                  withImage={withImage}
                />
              ))
            }
          </Container>
          {withImage &&
            <Container flex={0.7}/>
          }
        </Container>
        <Container flex={1}/>
      </Container>
    )
  }

  getNextOrders(orders) {
    const nextOrders = orders.length > 4 ? orders.slice(1, 4) : orders.slice(1, orders.length)
    while (nextOrders.length < 3) {
      nextOrders.push({})
    }

    return nextOrders
  }
}

ReadyOrdersBox.defaultProps = {
  flex: 1
}

ReadyOrdersBox.propTypes = {
  orders: PropTypes.array,
  flex: PropTypes.number,
  autoOrderCommand: PropTypes.object,
  format: PropTypes.string,
  withImage: PropTypes.bool
}

export default ReadyOrdersBox
