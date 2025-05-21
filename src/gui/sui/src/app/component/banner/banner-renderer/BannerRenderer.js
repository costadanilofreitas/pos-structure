import React from 'react'
import RendererChooser from '../../../../component/renderer-chooser'
import TotemRenderer from './TotemBannerRenderer'

export default function bannerRenderer(props) {
  return (
    <RendererChooser
      totem={<TotemRenderer {...props}/>}
    />
  )
}

