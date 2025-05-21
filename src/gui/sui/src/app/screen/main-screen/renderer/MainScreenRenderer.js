import React from 'react'
import RendererChooser from '../../../../component/renderer-chooser'
import { DefaultMainScreen, TotemMainScreen } from './JssMainScreen'

export default function MainScreenRenderer(props) {
  return (
    <RendererChooser
      mobile={<DefaultMainScreen {...props}/>}
      desktop={<DefaultMainScreen {...props}/>}
      totem={<TotemMainScreen {...props}/>}
    />
  )
}

