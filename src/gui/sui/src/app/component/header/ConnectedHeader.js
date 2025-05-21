import Header from './Header'
import withExecuteActionMessageBus from '../../../util/withExecuteActionMessageBus'
import withChangeMenu from '../../util/withChangeMenu'
import withState from '../../../util/withState'
import withStaticConfig from '../../util/withStaticConfig'


const stateHeader = withState(Header,
  'order',
  'operator',
  'workingMode',
  'posState',
  'selectedTable',
  'showTableInfo',
  'tableLists')

export default withStaticConfig(withExecuteActionMessageBus(withChangeMenu(stateHeader)))
