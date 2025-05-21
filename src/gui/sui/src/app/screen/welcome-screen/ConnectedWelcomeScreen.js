import WelcomeScreen from './WelcomeScreen'
import withExecuteActionMessageBus from '../../../util/withExecuteActionMessageBus'
import withStaticConfig from '../../util/withStaticConfig'

export default withStaticConfig(withExecuteActionMessageBus(WelcomeScreen))
