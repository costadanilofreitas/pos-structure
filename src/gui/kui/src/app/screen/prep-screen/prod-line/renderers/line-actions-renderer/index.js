import { bindActionCreators } from 'redux'

import LineActionsRenderer from './LineActionsRenderer'
import withState from '../../../../../../util/withState'
import { sendTouchCommandAction } from '../../../../../../actions'
import * as touchTypes from '../../../../../../constants/touchTypes'

function mapDispatchToProps(dispatch) {
  return bindActionCreators({
    setAsDoing: line => sendTouchCommandAction({
      name: touchTypes.TOUCH_DOING_LINE,
      payload: line
    }),
    setAsDone: line => sendTouchCommandAction({
      name: touchTypes.TOUCH_DONE_LINE,
      payload: line
    })
  }, dispatch)
}

export default withState(LineActionsRenderer, mapDispatchToProps)
