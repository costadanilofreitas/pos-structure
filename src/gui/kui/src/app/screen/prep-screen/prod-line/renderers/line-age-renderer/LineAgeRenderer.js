import React from 'react'
import PropTypes from 'prop-types'
import { KDSCellTimer } from '3s-posui/widgets'
import LinePropTypes from '../../../../../prop-types/LinePropTypes'
import { isAllWaiting } from '../../../../../../util/renderUtil'

export default function LineAgeRenderer({ line }) {
  let startTime = line.items[0].getLowestSendMoment()
  if (startTime == null || isAllWaiting(line.items)) {
    startTime = line.orderData.attributes.displayTime
  }
  return <KDSCellTimer startTime={startTime} interval={10}/>
}

LineAgeRenderer.propTypes = {
  line: LinePropTypes,
  classes: PropTypes.object
}
