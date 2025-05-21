import React from 'react'
import PropTypes from 'prop-types'
import RendererChooser from '../../../../component/renderer-chooser'
import { MobileRenderer, DesktopRenderer } from './JssTableListScreenRenderer'

export default function TableListScreenRenderer(props) {
  return (
    <RendererChooser
      mobile={<MobileRenderer {...props}/>}
      desktop={<DesktopRenderer {...props}/>}
      totem={<DesktopRenderer {...props}/>}
    />
  )
}

TableListScreenRenderer.propTypes = {
  children: PropTypes.oneOfType([PropTypes.array, PropTypes.object]),
  toggleLayout: PropTypes.func,
  toggleTableInfo: PropTypes.func,
  openTable: PropTypes.func,
  hasTables: PropTypes.bool
}
