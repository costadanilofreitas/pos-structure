import JssRecallScreenRenderer from './JssRecallScreenRenderer'
import withChangeMenu from '../../../util/withChangeMenu'
import withState from '../../../../util/withState'
import withStaticConfig from '../../../util/withStaticConfig'
import withExecuteActionMessageBus from '../../../../util/withExecuteActionMessageBus'
import { FETCH_STORED_ORDERS } from '../../../../constants/actionTypes'
import withDialogs from '../../../../util/withDialogs'


function mapDispatchToProps(dispatch) {
  return {
    updateStoredOrdersCount: (payload) => {
      dispatch({
        type: FETCH_STORED_ORDERS,
        payload: payload
      })
    }
  }
}

const connectedRenderer = withState(JssRecallScreenRenderer,
  mapDispatchToProps,
  'posId',
  'workingMode',
  'mobile',
  'actionRunning',
  'deviceType'
)

export default withDialogs(withStaticConfig(withChangeMenu(withExecuteActionMessageBus(connectedRenderer))))
