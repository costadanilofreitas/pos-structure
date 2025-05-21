import Chat from './Chat'
import withExecuteActionMessageBus from '../../../util/withExecuteActionMessageBus'
import withState from '../../../util/withState'

export default withExecuteActionMessageBus(withState(Chat, 'staticConfig'))
