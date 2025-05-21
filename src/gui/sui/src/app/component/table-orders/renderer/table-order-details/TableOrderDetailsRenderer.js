import React from 'react'
import PropTypes from 'prop-types'

import RendererChooser from '../../../../../component/renderer-chooser'
import WorkingModePropTypes from '../../../../../prop-types/WorkingModePropTypes'
import { DesktopTableOrderDetails, MobileTableOrderDetails } from './JssTableOrderDetails'


export default function TableOrderDetailsRenderer(props) {
  return (
    <RendererChooser
      mobile={<MobileTableOrderDetails {...props} />}
      desktop={<DesktopTableOrderDetails {...props} />}
      totem={<DesktopTableOrderDetails {...props} />}
    />
  )
}

TableOrderDetailsRenderer.propTypes = {
  orders: PropTypes.array,
  tableStatus: PropTypes.number.isRequired,
  workingMode: WorkingModePropTypes,
  currentTime: PropTypes.object,
  onOrderChange: PropTypes.func,
  onOrderCancel: PropTypes.func,
  onOrderPrint: PropTypes.func
}
