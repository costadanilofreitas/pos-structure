import OrderFunctions from './OrderFunctions'
import withState from '../../../util/withState'
import withExecuteActionMessageBus from '../../../util/withExecuteActionMessageBus'
import withChangeMenu from '../../util/withChangeMenu'
import withStaticConfig from '../../util/withStaticConfig'

export default withStaticConfig(withChangeMenu(withExecuteActionMessageBus(withState(OrderFunctions,
  'selectedTable',
  'workingMode',
  'order',
  'modifiers',
  'saleType',
  'theme'))))
