import ConfirmationScreen from './ConfirmationScreen'
import withState from '../../../util/withState'
import withExecuteActionMessageBus from '../../../util/withExecuteActionMessageBus'

export default withExecuteActionMessageBus(withState(ConfirmationScreen, 'staticConfig'))
