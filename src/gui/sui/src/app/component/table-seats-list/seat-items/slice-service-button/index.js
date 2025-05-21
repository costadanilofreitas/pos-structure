import SliceServiceButton from './SliceServiceButton'
import withExecuteActionMessageBus from '../../../../../util/withExecuteActionMessageBus'
import withState from '../../../../../util/withState'

export default withExecuteActionMessageBus(withState(SliceServiceButton, 'workingMode', 'selectedTable'))
