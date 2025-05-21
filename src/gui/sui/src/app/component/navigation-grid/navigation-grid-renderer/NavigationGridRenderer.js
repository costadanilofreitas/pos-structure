import React from 'react'
import RendererChooser from '../../../../component/renderer-chooser'
import { DesktopRenderer, TotemRenderer } from './JssNavigationGridRenderer'

export default function NavigationGridRenderer(props) {
  return (
    <RendererChooser
      mobile={<DesktopRenderer {...props}/>}
      desktop={<DesktopRenderer {...props}/>}
      totem={<TotemRenderer {...props}/>}
    />
  )
}

