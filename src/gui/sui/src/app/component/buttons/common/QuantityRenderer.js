import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { FlexChild } from '3s-widgets'
import { QuantityContainer } from './StyledCommonRenderer'


export default class QuantityRenderer extends Component {
  render() {
    const { quantity, quantityContainerSize, showQuantity, quantityContainerStyle } = this.props

    if (!showQuantity) {
      return null
    }

    return (
      <FlexChild size={quantityContainerSize}>
        <QuantityContainer style={quantityContainerStyle}>
          {this.showQuantity(quantity) && quantity}
        </QuantityContainer>
      </FlexChild>
    )
  }

  showQuantity(quantity) {
    return quantity != null && !isNaN(quantity) && quantity > 0
  }
}

QuantityRenderer.propTypes = {
  quantity: PropTypes.number,
  showQuantity: PropTypes.bool,
  quantityContainerSize: PropTypes.number,
  quantityContainerStyle: PropTypes.object
}
