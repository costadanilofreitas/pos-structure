import { EXECUTE_ACTION_REQUESTED, EXECUTE_ACTION_FINISHED } from '3s-posui/constants/actionTypes'

import OrderTenders from './OrderTenders'
import withState from '../../../util/withState'
import withShowDialog from '../../../util/withShowDialog'
import withStaticConfig from '../../util/withStaticConfig'
import withExecuteActionMessageBus from '../../../util/withExecuteActionMessageBus'

function mapDispatchToProps(dispatch) {
  return {
    actionRequest: function () {
      dispatch({ type: EXECUTE_ACTION_REQUESTED })
    },
    actionEnd: function () {
      dispatch({ type: EXECUTE_ACTION_FINISHED })
    }
  }
}

const orderTendersState = withState(OrderTenders,
  mapDispatchToProps,
  'order',
  'saleType',
  'selectedTable',
  'workingMode',
  'tefAvailable',
  'operator',
  'deviceType')

export default withShowDialog(withStaticConfig(withExecuteActionMessageBus(orderTendersState)))
