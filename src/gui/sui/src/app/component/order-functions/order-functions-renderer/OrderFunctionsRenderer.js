import React, { Component } from 'react'
import PropTypes from 'prop-types'

import RendererChooser from '../../../../component/renderer-chooser'
import { MobileRenderer, TotemRenderer, DesktopRenderer } from './JssOrderFunctionsRenderer'
import { shallowCompareEquals } from '../../../../util/renderUtil'
import OrderPropTypes from '../../../../prop-types/OrderPropTypes'


export default class OrderFunctionsRenderer extends Component {
  constructor(props) {
    super(props)
  }

  shouldComponentUpdate(nextProps) {
    if (nextProps.screenOrientation !== this.props.screenOrientation) {
      return true
    }

    const compProps = ['selectedTable', 'selectedSeat', 'isSalePanelVisible', 'isModifiersDisplayed', 'selectedParent']
    if (!shallowCompareEquals(this.props, nextProps, ...compProps)) {
      return true
    }

    const currOrder = this.props.order['@attributes']
    const nextOrder = nextProps.order['@attributes']
    if (currOrder == null || nextOrder == null) {
      return true
    }

    if (currOrder.state !== nextOrder.state) {
      return true
    }

    const currValidOrder = parseFloat(currOrder.totalAmount) > 0 && currOrder.state === 'IN_PROGRESS'
    const nextValidOrder = parseFloat(nextOrder.totalAmount) > 0 && nextOrder.state === 'IN_PROGRESS'

    return currValidOrder !== nextValidOrder
  }

  render() {
    return (
      <RendererChooser
        desktop={<DesktopRenderer {...this.props}/>}
        mobile={<MobileRenderer {...this.props}/>}
        totem={<TotemRenderer {...this.props}/>}
      />
    )
  }
}

OrderFunctionsRenderer.propTypes = {
  themes: PropTypes.object,
  order: OrderPropTypes,
  selectedSeat: PropTypes.number,
  isModifiersDisplayed: PropTypes.bool,
  isSalePanelVisible: PropTypes.bool,
  onAskBarcode: PropTypes.func,
  selectedLine: PropTypes.object,
  screenOrientation: PropTypes.number
}
