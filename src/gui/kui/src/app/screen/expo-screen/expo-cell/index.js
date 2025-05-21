import { bindActionCreators } from 'redux'

import ExpoCell from './ExpoCell'
import withState from '../../../../util/withState'
import { sendTouchCommandAction, sendBumpBarCommandAction } from '../../../../actions'
import * as touchTypes from '../../../../constants/touchTypes'

function mapDispatchToProps(dispatch) {
  return bindActionCreators({
    setCurrentOrder: index => sendTouchCommandAction({
      name: touchTypes.TOUCH_SET_CURRENT_ORDER,
      payload: index
    }),
    executeBumpCommand: (command, orderId) => sendBumpBarCommandAction({
      command: command,
      orderId: orderId
    })
  }, dispatch)
}


export default withState(ExpoCell, mapDispatchToProps, 'theme', 'timeDelta')
