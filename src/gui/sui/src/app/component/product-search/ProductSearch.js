import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'

import ProductSearchRenderer from './product-search-renderer'
import ActionButton from '../../../component/action-button'


class ProductSearch extends PureComponent {
  constructor(props) {
    super(props)

    this.state = {
      filteredProducts: this.getProducts(''),
      filter: ''
    }

    this.actionRenderer = this.actionRenderer.bind(this)
    this.handleSearch = this.handleSearch.bind(this)
  }

  render() {
    return (
      <ProductSearchRenderer
        posId={this.props.posId}
        onSellItem={this.props.onSellItem}
        actionRenderer={this.actionRenderer}
        handleSearch={this.handleSearch}
        filteredProducts={this.state.filteredProducts}
        filter={this.state.filter}
      />
    )
  }

  actionRenderer = (line) => {
    const { onSellItem, products } = this.props
    const rupturedProduct = products[line.rowData.plu].ruptured
    return (
      <ActionButton
        rounded={true}
        style={{ backgroundColor: '#b9663d', color: 'white', height: '4vh' }}
        executeAction={() => onSellItem(line)}
        text={rupturedProduct ? '$UNAVAILABLE' : '$SELL'}
        defaultText="Sell"
        blockOnActionRunning
        className={'test_ProductSearch_SELL'}
        disabled={rupturedProduct}
      />
    )
  }

  handleSearch = (filter) => {
    const filteredData = this.getProducts(filter || '')
    this.setState({
      filter,
      filteredProducts: filteredData
    })
  }

  getProducts = (filter) => {
    const products = this.getAvailableProducts()
    const searchFields = ['barcode', 'product_code', 'name']
    const filterStr = filter.toString()
    const filterLower = filterStr.toLowerCase()

    if (filterStr.length === 0) {
      return products
    }

    return this.filterProducts(products, searchFields, filter, filterLower)
  }

  getAvailableProducts() {
    const availableProductCodes = this.props.searchScreenItems.map(a => a.product_code)
    let products = Object.values(this.props.products)
    products = products.filter(x => availableProductCodes.includes(x.plu))

    return products
  }

  filterProducts(data, searchFields, filter, filterLower) {
    return _.filter(data, (obj) => {
      return _.some(searchFields, key => {
        const value = _.get(obj, key)
        return (
          value &&
          filter !== '' &&
          value.toString().toLowerCase().indexOf(filterLower) !== -1
        )
      })
    })
  }
}

ProductSearch.propTypes = {
  posId: PropTypes.number,
  onSellItem: PropTypes.func,
  products: PropTypes.object,
  groups: PropTypes.oneOfType([PropTypes.array, PropTypes.object]),
  searchScreenItems: PropTypes.array
}

export default ProductSearch
