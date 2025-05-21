import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { FlexChild } from '3s-widgets'
import { PriceBox, PriceBoxContainer } from './StyledCommonRenderer'
import Label from '../../../../component/label/Label'


export default class TextRenderer extends Component {
  render() {
    const { value, showValue, valueContainerSize, valueContainerStyle } = this.props

    if (!showValue) {
      return null
    }

    return (
      <FlexChild size={valueContainerSize}>
        <PriceBoxContainer style={valueContainerStyle}>
          <PriceBox>
            {value > 0 &&
            <Label
              key="orderTotalAmount"
              text={value}
              style="currency"
            />
            }
          </PriceBox>
        </PriceBoxContainer>
      </FlexChild>
    )
  }
}

TextRenderer.propTypes = {
  value: PropTypes.number,
  showValue: PropTypes.bool,
  valueContainerSize: PropTypes.number,
  valueContainerStyle: PropTypes.object
}
