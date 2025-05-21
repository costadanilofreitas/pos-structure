import React, { Component } from 'react'
import { connect } from 'react-redux'
import PropTypes from 'prop-types'

import NavigationGrid from '../navigation-grid'
import { shallowIgnoreEquals } from '../../../util/renderUtil'
import ProductButton from '../buttons/product-button'
import DeviceType from '../../../constants/Devices'


class ProductGrid extends Component {
  constructor(props) {
    super(props)

    this.handleRenderSaleButton = this.handleRenderSaleButton.bind(this)
  }

  shouldComponentUpdate(nextProps) {
    return !shallowIgnoreEquals(this.props, nextProps, 'sellItem', 'classes')
  }

  render() {
    const { rows, columns } = this.props

    return (
      <NavigationGrid
        groups={this.props.groups}
        sellFunc={this.props.sellItem}
        cols={columns}
        rows={rows}
        expandCol={columns}
        groupsPerCol={2}
        maxSpanCols={3}
        styleTitle={{ fontSize: '1.3vh', color: 'black' }}
        buttonProps={{ blockOnActionRunning: true }}
        onRenderSaleButton={this.handleRenderSaleButton}
      />
    )
  }

  handleRenderSaleButton(item, key, showImage, showValue, addBgColor, sellFunc) {
    const functionHandler = () => sellFunc(item)
    const { deviceType } = this.props
    const removeBorder = { border: 'none', borderRadius: '0', boxShadow: 'none', fontSize: '80%' }

    return (
      <ProductButton
        code={item.product_code}
        bgColor={item.background_color}
        addBgColor={addBgColor}
        buttonSpacing={deviceType === DeviceType.Totem ? '5%' : '0.4vmin'}
        buttonStyle={deviceType === DeviceType.Totem ? { height: '25vmin' } : {}}
        mainContainerStyle={deviceType !== DeviceType.Totem ? removeBorder : { background: '#FFFFFF', fontSize: '1.5vmin' }}
        isTotem={deviceType === DeviceType.Totem}
        showQuantity={false}
        showImage={deviceType === DeviceType.Totem}
        showValue={deviceType === DeviceType.Totem}
        onClick={functionHandler}
      >
      </ProductButton>
    )
  }
}

function mapStateToProps(state) {
  return {
    rows: parseInt((state.staticConfig.productsScreenDimensions || { rows: 9 }).rows, 10),
    columns: parseInt((state.staticConfig.productsScreenDimensions || { columns: 9 }).columns, 10)
  }
}

ProductGrid.propTypes = {
  groups: PropTypes.oneOfType([PropTypes.array, PropTypes.object]),
  sellItem: PropTypes.func,
  rows: PropTypes.number,
  columns: PropTypes.number,
  deviceType: PropTypes.number
}

export default connect(mapStateToProps, null)(ProductGrid)
