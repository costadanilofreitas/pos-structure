import React from 'react'
import PropTypes from 'prop-types'
import RendererChooser from '../../../../component/renderer-chooser'
import { MobileRenderer, DesktopRenderer } from './JssLoginScreenRenderer'

export default function LoginScreenRenderer(props) {
  return (
    <RendererChooser
      mobile={<MobileRenderer {...props}/>}
      desktop={<DesktopRenderer {...props}/>}
      totem={<DesktopRenderer {...props}/>}
    />
  )
}

LoginScreenRenderer.propTypes = {
  children: PropTypes.oneOfType([PropTypes.array, PropTypes.object])
}
