import React from 'react'
import RendererChooser from '../../../../component/renderer-chooser'
import { DesktopProductSearchRenderer, MobileProductSearchRenderer } from './index'

export default function ProductSearchRenderer(props) {
  return (
    <RendererChooser
      desktop={<DesktopProductSearchRenderer {...props}/>}
      mobile={<MobileProductSearchRenderer {...props}/>}
    />
  )
}
