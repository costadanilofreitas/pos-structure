import React from 'react'
import RendererChooser from '../../../../component/renderer-chooser'
import { DesktopRenderer, MobileRenderer, TotemRenderer } from './JssOrderScreenRenderer'


export default function OrderScreenRenderer(props) {
  return (
    <RendererChooser
      desktop={<DesktopRenderer {...props}/>}
      mobile={<MobileRenderer {...props}/>}
      totem={<TotemRenderer {...props}/>}
    />
  )
}
