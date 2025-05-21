import MainScreen from './MainScreen'
import withState from '../../../util/withState'
import withExecuteActionMessageBus from '../../../util/withExecuteActionMessageBus'
import withStaticConfig from '../../util/withStaticConfig'
import withChangeMenu from '../../util/withChangeMenu'


export default withChangeMenu(withStaticConfig(withExecuteActionMessageBus(withState(MainScreen,
  'operator',
  'selectedMenu',
  'selectedTable',
  'workingMode',
  'order.state',
  'actionRunning',
  'posState',
  'deviceType',
  'order',
  'infoMessage',
  'staticConfig',
  'screenOrientation'))))
