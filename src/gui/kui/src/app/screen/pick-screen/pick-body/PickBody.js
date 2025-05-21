import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { FlexGrid, Image } from '3s-widgets'

import { BackgroundDiv, Container, MainOrderContainer, ReadyAndCalledOrdersContainer } from './StyledPickBody'
import ReadyOrdersBox from '../pick-orders/ReadyOrdersBox'
import CalledOrdersBox from '../pick-orders/CalledOrdersBox'

import { getCurrentOrders } from '../../../util'
import { deepEquals } from '../../../../util/renderUtil'

class PickBody extends Component {
  constructor(props) {
    super(props)

    this.pick_background_image = this.getImage()
  }

  shouldComponentUpdate(nextProps) {
    if (this.props.orders.length !== nextProps.orders.length) {
      return true
    } else if (nextProps.orders.length !== 0) {
      return !deepEquals(nextProps.orders, this.props.orders)
    }

    return false
  }

  render() {
    const { theme, kdsModel, orders } = this.props
    const currentOrders = getCurrentOrders(orders).reverse()
    const readyOrders = this.getReadyOrders(currentOrders)
    const calledOrders = this.getCalledOrders(currentOrders)
    const autoOrderCommand = kdsModel.autoOrderCommand
    const format = kdsModel.cellFormat.body
    const withImage = this.pick_background_image != null

    return (
      <Container theme={theme}>
        <BackgroundDiv withImage={withImage}>
          <Image
            src={['./images/PickupBackground.png', this.pick_background_image]}
            containerHeight={'100%'}
            containerWidth={'100%'}
            imageWidth={'100%'}
            imageHeight={'100%'}
            background={'transparent'}
            objectFit={'fill'}
          />
        </BackgroundDiv>
        <FlexGrid direction={'column'}>
          <MainOrderContainer>
            <ReadyAndCalledOrdersContainer>
              <ReadyOrdersBox
                orders={readyOrders}
                format={format}
                theme={theme}
                flex={16}
                autoOrderCommand={autoOrderCommand}
                withImage={withImage}
              />
              <CalledOrdersBox
                orders={calledOrders}
                format={format}
                theme={theme}
                flex={7}
                autoOrderCommand={autoOrderCommand}
                withImage={withImage}
              />
              <Container flex={1}/>
            </ReadyAndCalledOrdersContainer>
          </MainOrderContainer>
        </FlexGrid>
      </Container>
    )
  }

  getImage() {
    try {
      return require('../../../../../images/pick_background.png')
    } catch (err) {
      return null
    }
  }

  getReadyOrders(orders) {
    return orders.length > 4 ? orders.slice(0, 4) : orders.slice(0, orders.length)
  }

  getCalledOrders(orders) {
    if (orders.length > 12) {
      return orders.slice(4, 12)
    } else if (orders.length > 4) {
      return orders.slice(4, orders.length)
    }

    return []
  }
}

PickBody.propTypes = {
  kdsModel: PropTypes.object,
  orders: PropTypes.array,
  theme: PropTypes.object
}

PickBody.defaultProps = {
  orders: []
}

export default PickBody
