import React from 'react'
import PropTypes from 'prop-types'

import ProductButton from '../../buttons/product-button'
import ActionButton from '../../../../component/action-button'
import Button from '../../../../component/action-button/Button'

const defaultButtonStyle = { fontSize: '2vmin' }

export default function NavigationItemRenderer({ item, onClick, classes, showPrices, isNavigation }) {
  function hasBackgroundColor() {
    return item.background_color != null
  }

  function sonHasBackgroundColor() {
    return item.items != null &&
           item.items.length > 0 &&
           item.items[0].background_color != null
  }

  function getBackgroundColor() {
    if (sonHasBackgroundColor()) {
      return item.items[0].background_color
    } else if (hasBackgroundColor()) {
      return item.background_color
    }
    return null
  }

  const bgColor = getBackgroundColor()
  if (bgColor != null) {
    const style = { ...defaultButtonStyle, boxShadow: '1px 1px darkgray', borderRadius: '10px', backgroundColor: bgColor }
    return (
      <div className={!isNavigation ? classes.category : classes.categoryWithBorder}>
        {!isNavigation ?
          <ProductButton
            addBgColor
            bgColor={bgColor}
            showValue={showPrices}
            code={item.product_code}
            text={item.button_text}
            onClick={() => onClick(item)}
            textContainerStyle={defaultButtonStyle}
            buttonStyle={{ borderRadius: 10 }}
            mainContainerStyle={style}
          />
          :
          <Button style={style} onClick={() => onClick(item)}>
            {item.button_text}
          </Button>
        }
      </div>
    )
  }

  return !isNavigation ? (
    <ProductButton
      buttonStyle={defaultButtonStyle}
      showValue={showPrices}
      code={item.product_code}
      onClick={() => onClick(item)}
    />
  ) : (
    <ActionButton
      key={item.name}
      style={defaultButtonStyle}
      onClick={() => onClick(item)}
    >
      {item.button_text}
    </ActionButton>
  )
}

NavigationItemRenderer.propTypes = {
  item: PropTypes.shape({
    name: PropTypes.string,
    button_text: PropTypes.string,
    background_color: PropTypes.string,
    product_code: PropTypes.string,
    classes: PropTypes.arrayOf(PropTypes.string),
    items: PropTypes.array
  }),
  onClick: PropTypes.func,
  classes: PropTypes.object,
  showPrices: PropTypes.bool,
  isNavigation: PropTypes.bool
}
