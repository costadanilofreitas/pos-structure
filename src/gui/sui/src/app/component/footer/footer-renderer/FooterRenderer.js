import React from 'react'
import RendererChooser from '../../../../component/renderer-chooser'
import { DesktopRenderer, MobileRenderer, TotemRenderer } from './JssFooterRenderer'

export default function footerRenderer(props) {
  return (
    <RendererChooser
      mobile={<MobileRenderer {...props}/>}
      desktop={<DesktopRenderer {...props}/>}
      totem={<TotemRenderer {...props}/>}
    />
  )
}

