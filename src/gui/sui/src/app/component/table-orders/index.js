import TableOrders from './TableOrders'
import withGetCurrentDate from '../../../util/withGetCurrentDate'
import withExecuteActionMessageBus from '../../../util/withExecuteActionMessageBus'
import withState from '../../../util/withState'

export default withExecuteActionMessageBus(withGetCurrentDate(withState(TableOrders, 'workingMode')))
