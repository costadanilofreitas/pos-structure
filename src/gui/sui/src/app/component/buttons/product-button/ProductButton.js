import React, { Component } from 'react'
import PropTypes from 'prop-types'
import has from 'lodash/has'

import { FlexGrid } from '3s-widgets'
import { ButtonContent, MainContainer } from '../common/StyledCommonRenderer'
import QuantityRenderer from '../common/QuantityRenderer'
import ImageRenderer from '../common/ImageRenderer'
import TextRenderer from '../common/TextRenderer'
import ValueRenderer from '../common/ValueRenderer'
import UnavailableTextRenderer from '../common/UnavailableTextRenderer'


function getContextAndPartCode(code) {
  const lastContextSeparator = code.lastIndexOf('.')
  if (lastContextSeparator === -1) {
    return [null, code]
  }
  return [code.slice(0, lastContextSeparator), code.slice(lastContextSeparator + 1)]
}

function getProductPrice(product, context) {
  if (product == null || product.price == null) {
    return 0
  }
  let currentContext = context
  while (currentContext) {
    if (has(product.price, currentContext)) {
      return product.price[currentContext]
    }
    const lastIndexSeparator = currentContext.indexOf('.')
    if (lastIndexSeparator === -1) {
      break
    }
    currentContext = currentContext.slice(lastIndexSeparator + 1)
  }
  return product.price.null || 0
}

export default class ProductButton extends Component {
  render() {
    const {
      showImage, bgColor, addBgColor, onClick, selected, imageContainerSize, textContainerSize, showValue, showText,
      valueContainerSize, buttonSpacing, buttonStyle, mainContainerStyle, quantity, quantityContainerSize, showQuantity,
      direction, quantityContainerStyle, imageContainerStyle, textContainerStyle, valueContainerStyle, products, code,
      theme, showSelectedBorderBottom, isTotem
    } = this.props
    const [context, partCode] = getContextAndPartCode(code)
    const product = Object.keys(products).includes(partCode) ? products[partCode] : null
    const productImage = product != null ? `PRT${partCode.toString().padStart(8, '0')}` : null
    const productName = product != null ? product.name : null
    const productValue = getProductPrice(product, context)
    const color = this.getColor(product, addBgColor, bgColor)
    const ruptured = product != null && product.ruptured

    if (isTotem) {
      buttonStyle.color = theme.fontColor
    }

    return (
      <ButtonContent
        className={`test_ProductButton_${productName != null ? productName.replace(/\s/g, '-') : ''}`}
        style={buttonStyle}
        onClick={() => ruptured ? '' : onClick()}
        isTotem={isTotem}
        showImage={showImage}
        buttonSpacing={buttonSpacing}
        color={color}
        ruptured={ruptured}
      >
        <MainContainer
          ruptured={ruptured}
          isTotem={isTotem}
          selected={selected}
          showImage={showImage}
          style={mainContainerStyle}
          theme={theme}
          showSelectedBorderBottom={showSelectedBorderBottom}
        >
          <FlexGrid direction={direction}>
            <QuantityRenderer
              showQuantity={showQuantity}
              quantity={quantity}
              quantityContainerSize={quantityContainerSize}
              quantityContainerStyle={quantityContainerStyle}
            />
            <ImageRenderer
              showImage={showImage}
              imageName={productImage}
              imageContainerSize={imageContainerSize}
              imageContainerStyle={imageContainerStyle}
            />
            <TextRenderer
              showText={showText}
              text={productName}
              textContainerSize={textContainerSize}
              textContainerStyle={textContainerStyle}
            />
            <ValueRenderer
              showValue={showValue && !ruptured}
              value={productValue}
              valueContainerSize={valueContainerSize}
              valueContainerStyle={valueContainerStyle}
            />
            <UnavailableTextRenderer
              enabled={ruptured}
              unavailableTextSize={2}
            />
          </FlexGrid>
        </MainContainer>
      </ButtonContent>
    )
  }

  getColor(product, addBgColor, bgColor) {
    if (product != null && product.ruptured) {
      return this.props.theme.productDisabledBackground
    }

    return addBgColor ? bgColor : 'transparent'
  }
}

ProductButton.propTypes = {
  quantity: PropTypes.number,
  quantityContainerSize: PropTypes.number,
  showQuantity: PropTypes.bool,

  imageContainerSize: PropTypes.number,
  showImage: PropTypes.bool,

  textContainerSize: PropTypes.number,
  showText: PropTypes.bool,

  valueContainerSize: PropTypes.number,
  showValue: PropTypes.bool,

  code: PropTypes.string,
  bgColor: PropTypes.string,
  addBgColor: PropTypes.bool,
  selected: PropTypes.bool,
  onClick: PropTypes.func,
  products: PropTypes.object,
  theme: PropTypes.object,

  buttonSpacing: PropTypes.string,
  direction: PropTypes.string,
  buttonStyle: PropTypes.object,
  mainContainerStyle: PropTypes.object,
  quantityContainerStyle: PropTypes.object,
  imageContainerStyle: PropTypes.object,
  textContainerStyle: PropTypes.object,
  valueContainerStyle: PropTypes.object,
  showSelectedBorderBottom: PropTypes.bool,
  isTotem: PropTypes.bool
}

ProductButton.defaultProps = {
  quantity: null,
  quantityContainerSize: 1,
  showQuantity: false,

  imageContainerSize: 6,
  showImage: false,

  textContainerSize: 4,
  showText: true,

  valueContainerSize: 2,
  showValue: false,

  code: '',
  bgColor: '#FFFFFF',
  addBgColor: true,
  selected: false,

  buttonSpacing: '0px',
  direction: 'column',
  buttonStyle: {},
  mainContainerStyle: {},
  quantityContainerStyle: {},
  imageContainerStyle: {},
  textContainerStyle: {},
  valueContainerStyle: {},
  showSelectedBorderBottom: false,
  isTotem: false
}
