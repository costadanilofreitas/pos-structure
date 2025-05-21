import RuptureDialog from './RuptureDialog'
import withExecuteActionMessageBus from '../../../util/withExecuteActionMessageBus'
import withState from '../../../util/withState'

export default withExecuteActionMessageBus(withState(RuptureDialog, 'products'))
