import React from 'react'
import PropTypes from 'prop-types'
import MessageBusPropTypes from '../../../../prop-types/MessageBusPropTypes'
import OrderPropTypes from '../../../../prop-types/OrderPropTypes'
import RendererChooser from '../../../../component/renderer-chooser'
import { DesktopRenderer, MobileRenderer, TotemRenderer } from './JssTenderScreenRenderer'
import StaticConfigPropTypes from '../../../../prop-types/StaticConfigPropTypes'

export default function TenderScreenRenderer(props) {
  return (
    <RendererChooser
      mobile={<MobileRenderer {...props}/>}
      desktop={<DesktopRenderer {...props}/>}
      totem={<TotemRenderer {...props}/>}
    />
  )
}

TenderScreenRenderer.propTypes = {
  classes: PropTypes.object,
  children: PropTypes.arrayOf(PropTypes.object),
  tefAvailable: PropTypes.bool,
  msgBus: MessageBusPropTypes,
  order: OrderPropTypes,
  staticConfig: StaticConfigPropTypes,
  customOrder: OrderPropTypes,
  toggleTenderScreen: PropTypes.func
}
