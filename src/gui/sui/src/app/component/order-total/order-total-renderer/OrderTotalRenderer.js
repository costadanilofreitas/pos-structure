import React from 'react'
import RendererChooser from '../../../../component/renderer-chooser'
import { DesktopOrderTotalRenderer, MobileOrderTotalRenderer, TotemOrderTotalRenderer } from './index'

export default function OrderTotalRenderer(props) {
  return (
    <RendererChooser
      mobile={<MobileOrderTotalRenderer {...props}/>}
      desktop={<DesktopOrderTotalRenderer {...props}/>}
      totem={<TotemOrderTotalRenderer {...props}/>}
    />
  )
}
