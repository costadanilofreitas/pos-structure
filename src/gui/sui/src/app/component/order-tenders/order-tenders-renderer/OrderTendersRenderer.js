import React from 'react'
import RendererChooser from '../../../../component/renderer-chooser'
import MobileDesktopTendersRenderer from './MobileDesktopTendersRenderer'
import TotemTendersRenderer from './TotemTendersRenderer'

export default function OrderTendersRenderer(props) {
  return (
    <RendererChooser
      mobile={<MobileDesktopTendersRenderer {...props}/>}
      desktop={<MobileDesktopTendersRenderer {...props}/>}
      totem={<TotemTendersRenderer {...props}/>}
    />
  )
}
