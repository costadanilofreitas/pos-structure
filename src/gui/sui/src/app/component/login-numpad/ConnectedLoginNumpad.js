import LoginNumpad from './LoginNumpad'
import withExecuteActionMessageBus from '../../../util/withExecuteActionMessageBus'
import withState from '../../../util/withState'

export default withExecuteActionMessageBus(withState(LoginNumpad, 'workingMode', 'operator', 'posState'))
