import React, { Component } from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'

import { ensureArray } from '3s-posui/utils'

import ItemModifier from '../../../../component/item-modifier'
import ProductSearch from '../../../../component/product-search'
import BarcodeScreen from '../../../../component/barcode-screen'
import ProductGrid from '../../../../component/product-grid'
import OrderPropTypes from '../../../../../prop-types/OrderPropTypes'


export default class ProductsContainer extends Component {
  constructor(props) {
    super(props)

    this.getProductSearch = this.getProductSearch.bind(this)
    this.getBarcodeScreen = this.getBarcodeScreen.bind(this)
    this.getProductScreen = this.getProductScreen.bind(this)
    this.getModifierItems = this.getModifierItems.bind(this)
  }

  render() {
    return (
      <div style={{ height: '100%', width: '100%' }}>
        {this.getProductSearch()}
        {this.getBarcodeScreen()}
        {this.getProductScreen()}
        {this.getModifierItems()}
      </div>
    )
  }

  getProductSearch() {
    const { showSearch, onSellItem, groups, searchScreenItems } = this.props

    return showSearch ?
      <ProductSearch groups={groups} onSellItem={onSellItem} searchScreenItems={searchScreenItems}/> : null
  }

  getBarcodeScreen() {
    const { selectedLine, selectedQty, showBarcodeScreen, onAskBarcode, handleOnSellByBarcode, order } = this.props

    if (!showBarcodeScreen) {
      return null
    }
    return (
      <BarcodeScreen
        selectedLine={selectedLine}
        onAskBarcode={onAskBarcode}
        selectedQty={selectedQty}
        handleOnSellByBarcode={handleOnSellByBarcode}
        order={order}
      />
    )
  }

  getProductScreen() {
    const { isModifiersDisplayed, groups, showSearch, onSellItem, showBarcodeScreen } = this.props
    const showProducts = !showSearch && !isModifiersDisplayed && !showBarcodeScreen

    return showProducts ? <ProductGrid sellItem={onSellItem} groups={groups}/> : null
  }

  getModifierItems() {
    const { isModifiersDisplayed } = this.props
    if (!isModifiersDisplayed) {
      return null
    }

    const { selectedLine, order } = this.props
    let filteredSaleLines = []
    if (order.SaleLine != null) {
      filteredSaleLines = _.filter(ensureArray(order.SaleLine), saleLine => {
        return selectedLine != null ? selectedLine.lineNumber === saleLine['@attributes'].lineNumber : {}
      })
    }

    const { onLineClick, selectedQty, onQtyChange, onSellOption, onSellModifier, voidOrClearOption } = this.props
    return (
      <ItemModifier
        saleLines={filteredSaleLines}
        selectedLine={selectedLine}
        onSellOption={onSellOption}
        voidOrClearOption={voidOrClearOption}
        onSellModifier={onSellModifier}
        autoExitModifierScreen={true}
        selectedQty={selectedQty}
        onQtyChange={onQtyChange}
        onLineClick={onLineClick}
      />
    )
  }
}

ProductsContainer.propTypes = {
  order: OrderPropTypes,
  selectedLine: PropTypes.object,
  onLineClick: PropTypes.func,
  selectedQty: PropTypes.number,
  onQtyChange: PropTypes.func,
  onAskBarcode: PropTypes.func,
  isModifiersDisplayed: PropTypes.bool,
  groups: PropTypes.oneOfType([PropTypes.array, PropTypes.object]),
  showSearch: PropTypes.bool,
  showBarcodeScreen: PropTypes.bool,
  onSellItem: PropTypes.func,
  onSellOption: PropTypes.func,
  onSellModifier: PropTypes.func,
  voidOrClearOption: PropTypes.func,
  handleOnSellByBarcode: PropTypes.func,
  searchScreenItems: PropTypes.array
}
