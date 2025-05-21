import LoginInfo from './LoginInfo'
import withExecuteActionMessageBus from '../../../util/withExecuteActionMessageBus'
import withState from '../../../util/withState'
import withGetCurrentDate from '../../../util/withGetCurrentDate'

export default withGetCurrentDate(
  withExecuteActionMessageBus(
    withState(LoginInfo, 'operator', 'posState', 'workingMode')))
