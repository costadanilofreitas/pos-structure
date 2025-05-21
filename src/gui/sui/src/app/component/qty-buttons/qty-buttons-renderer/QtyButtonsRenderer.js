import React from 'react'
import RendererChooser from '../../../../component/renderer-chooser'
import { DesktopQtyButtonsRenderer, MobileQtyButtonsRenderer } from './index'

export default function QtyButtonsRenderer(props) {
  return (
    <RendererChooser
      desktop={<DesktopQtyButtonsRenderer {...props}/>}
      mobile={<MobileQtyButtonsRenderer {...props}/>}
      totem={<DesktopQtyButtonsRenderer {...props}/>}
    />
  )
}
