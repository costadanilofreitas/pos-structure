import { bindActionCreators } from 'redux'

import ProdLine from './ProdLine'
import withState from '../../../../util/withState'
import { sendTouchCommandAction } from '../../../../actions'
import * as touchTypes from '../../../../constants/touchTypes'

function mapDispatchToProps(dispatch) {
  return bindActionCreators({
    selectLine: lineNumber => sendTouchCommandAction(({
      name: touchTypes.TOUCH_SELECT_LINE,
      payload: lineNumber
    }))
  }, dispatch)
}

export default withState(ProdLine, mapDispatchToProps, 'kdsModel', 'currentLine', 'zoom', 'timeDelta')
