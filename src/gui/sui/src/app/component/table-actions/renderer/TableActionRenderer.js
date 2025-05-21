import React from 'react'
import PropTypes from 'prop-types'

import RendererChooser from '../../../../component/renderer-chooser'
import TablePropTypes from '../../../../prop-types/TablePropTypes'
import { DesktopTableActionsRenderer, MobileTableActionRenderer } from './JssTableActionsRenderer'


export default function TableActionRenderer(props) {
  return (
    <RendererChooser
      mobile={<MobileTableActionRenderer {...props} />}
      desktop={<DesktopTableActionsRenderer {...props} />}
      totem={<DesktopTableActionsRenderer {...props} />}
    />
  )
}

TableActionRenderer.propTypes = {
  tableActions: PropTypes.array,
  table: TablePropTypes
}
