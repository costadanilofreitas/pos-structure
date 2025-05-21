import OrderScreen from './ConnectedOrderScreen'
import withDialogs from '../../../util/withDialogs'
import withMessageBus from '../../../util/withMessageBus'

export default withDialogs(withMessageBus(OrderScreen))
