import React, { Component } from 'react'
import PropTypes from 'prop-types'
import SaleTypeRenderer from './sale-type-renderer'
import { orderHasAttribute } from '../../util/orderValidator'
import StaticConfigPropTypes from '../../../prop-types/StaticConfigPropTypes'
import RendererChooser from '../../../component/renderer-chooser'
import TotemSaleTypeRenderer from './totem-renderer'


export default class SaleType extends Component {
  constructor(props) {
    super(props)

    this.setSaleType = this.setSaleType.bind(this)
    this.handleOnSaleTypeClick = this.handleOnSaleTypeClick.bind(this)
  }

  componentDidMount() {
    this.setSaleType()
  }

  shouldComponentUpdate(nextProps) {
    if (this.props.saleType !== nextProps.saleType) {
      return true
    }

    if (nextProps.screenOrientation !== this.props.screenOrientation) {
      return true
    }

    const currOrder = this.props.order || {}
    const nextOrder = nextProps.order || {}
    return currOrder.state !== nextOrder.state || currOrder.saleTypeDescr !== nextOrder.saleTypeDescr
  }

  render() {
    const rendererProps = {
      saleType: this.props.saleType,
      onSaleTypeClick: this.handleOnSaleTypeClick,
      availableSaleTypes: this.props.staticConfig.availableSaleTypes,
      order: this.props.order,
      screenOrientation: this.props.screenOrientation
    }

    return (
      <RendererChooser
        desktop={<SaleTypeRenderer {...rendererProps} />}
        mobile={<SaleTypeRenderer {...rendererProps} />}
        totem={<TotemSaleTypeRenderer {...rendererProps} />}
      />
    )
  }

  isValidOrderSaleType() {
    const order = this.props.order
    const hasSaleType = orderHasAttribute(this.props.order, 'saleTypeDescr')
    const isValidSaleType = hasSaleType && order['@attributes'].saleTypeDescr !== ''
    const isValidOrderState = order.state === 'IN_PROGRESS'

    return hasSaleType && isValidSaleType && isValidOrderState
  }

  getFirstAvailableSaleType(allSaleTypes) {
    return _.flatten(allSaleTypes)[0]
  }

  setSaleType() {
    let allSaleTypes = this.props.staticConfig.availableSaleTypes
    if (allSaleTypes == null || allSaleTypes.length === 0) {
      allSaleTypes = [['EAT_IN']]
    }

    let saleType = this.getFirstAvailableSaleType(allSaleTypes)
    if (this.isValidOrderSaleType()) {
      saleType = this.props.order['@attributes'].saleTypeDescr
    }

    this.props.changeSaleType(saleType.toString())
  }

  handleOnSaleTypeClick(saleType) {
    if (this.isValidOrderSaleType()) {
      this.props.msgBus.syncAction('doChangeSaleType', saleType)
        .then(response => {
          if (response.ok && response.data === 'True') {
            this.props.changeSaleType(saleType)
          }
        })
    } else {
      this.props.changeSaleType(saleType)
    }
  }
}

SaleType.propTypes = {
  order: PropTypes.object,
  saleType: PropTypes.string,
  changeSaleType: PropTypes.func,
  msgBus: PropTypes.shape({
    syncAction: PropTypes.func.isRequired
  }),
  staticConfig: StaticConfigPropTypes,
  screenOrientation: PropTypes.number
}
