import { bindActionCreators } from 'redux'

import KdsFooter from './KdsFooter'
import withState from '../../../util/withState'

import {
  sendTouchCommandAction
} from '../../../actions'
import * as touchTypes from '../../../constants/touchTypes'


function mapDispatchToProps(dispatch) {
  return bindActionCreators({
    handleGoToNextPage: () => sendTouchCommandAction({
      name: touchTypes.TOUCH_NEXT_PAGE
    }),
    handleGoToPreviousPage: () => sendTouchCommandAction({
      name: touchTypes.TOUCH_PREVIOUS_PAGE
    })
  }, dispatch)
}


export default withState(KdsFooter, mapDispatchToProps, 'kdsModel', 'paginationBlockSize')
