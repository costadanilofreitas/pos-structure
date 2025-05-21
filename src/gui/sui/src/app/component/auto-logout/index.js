import AutoLogout from './AutoLogout'
import withState from '../../../util/withState'
import withDialogs from '../../../util/withDialogs'
import withStaticConfig from '../../util/withStaticConfig'
import withChangeDialog from '../../util/withChangeDialog'
import withAbandonPos from '../../util/withAbandonPos'
import withCloseDialog from '../../util/withCloseDialog'


export default withDialogs(withAbandonPos(withCloseDialog(withChangeDialog(withStaticConfig(withState(AutoLogout,
  'operator',
  'selectedTable',
  'order',
  'posState',
  'deviceType',
  'actionRunning'))))))
