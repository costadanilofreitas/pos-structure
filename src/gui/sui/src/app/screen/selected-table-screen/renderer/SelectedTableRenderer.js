import React from 'react'
import PropTypes from 'prop-types'

import RendererChooser from '../../../../component/renderer-chooser'
import MobileSelectedTableRenderer from './MobileSelectedTableRenderer'
import DesktopSelectedTableRenderer from './DesktopSelectedTableRenderer'
import TablePropTypes from '../../../../prop-types/TablePropTypes'

export default function SelectedTableRenderer(props) {
  return (
    <RendererChooser
      mobile={<MobileSelectedTableRenderer {...props}/>}
      desktop={<DesktopSelectedTableRenderer {...props}/>}
      totem={<DesktopSelectedTableRenderer {...props}/>}
    />
  )
}

SelectedTableRenderer.propTypes = {
  selectedTable: TablePropTypes,
  mirror: PropTypes.bool,
  children: PropTypes.oneOfType([PropTypes.array, PropTypes.object])
}
