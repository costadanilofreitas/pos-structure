import React from 'react'
import PropTypes from 'prop-types'

import { DesktopTableOrdersRenderer, MobileTableOrdersRenderer } from './JssTableOrdersRenderer'
import RendererChooser from '../../../../component/renderer-chooser'
import WorkingModePropTypes from '../../../../prop-types/WorkingModePropTypes'


export default function TableOrdersRenderer(props) {
  return (
    <RendererChooser
      mobile={<MobileTableOrdersRenderer {...props} />}
      desktop={<DesktopTableOrdersRenderer {...props} />}
      totem={<DesktopTableOrdersRenderer {...props} />}
    />
  )
}

TableOrdersRenderer.propTypes = {
  orders: PropTypes.array,
  status: PropTypes.number.isRequired,
  workingMode: WorkingModePropTypes,
  currentTime: PropTypes.object,
  onOrderChange: PropTypes.func,
  onOrderCancel: PropTypes.func,
  onOrderPrint: PropTypes.func
}
