import React from 'react'
import PropTypes from 'prop-types'
import { KDSCellTimer } from '3s-posui/widgets'
import LinePropTypes from '../../../../../prop-types/LinePropTypes'
import {
  getMostRecentDoing,
  getNotDoneLowestSendMoment,
  isAllWaiting,
  getDoingTime,
  isAllDone,
  firstItemIsDoingOrDone,
  firstItemIsDone
} from '../../../../../../util/renderUtil'

export default function LineCookTimeRenderer({ line }) {
  const currentItems = line.items.filter(x => !x.tags.includes('dont-need-cook'))
  const waitingItems = currentItems.filter(x => x.tags.includes('wait-prep-time'))
  const doingTime = getDoingTime(currentItems)

  if ((doingTime === null && waitingItems.length === 0) || isAllDone(currentItems)) {
    return <span>-</span>
  }
  const timeStamp = getMostRecentDoing(currentItems)

  if ((doingTime != null && !isAllDone(currentItems))) {
    if (firstItemIsDoingOrDone(currentItems)) {
      const time = !firstItemIsDone(currentItems) && timeStamp !== null ? timeStamp : doingTime
      return <KDSCellTimer startTime={time} isGMT={false}/>
    }
  }
  const sendMoment = getNotDoneLowestSendMoment(waitingItems)

  if (isAllWaiting(waitingItems) && sendMoment != null) {
    return <KDSCellTimer startTime={sendMoment} isGMT={false} backwards={true}/>
  }

  return <span>-</span>
}

LineCookTimeRenderer.propTypes = {
  line: LinePropTypes,
  classes: PropTypes.object
}
