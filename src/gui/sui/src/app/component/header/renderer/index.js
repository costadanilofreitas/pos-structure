import HeaderRenderer from './JssRenderer'
import withState from '../../../../util/withState'
import withStoredOrders from '../../../../util/withStoredOrders'

export default withStoredOrders(withState(HeaderRenderer, 'mobile', 'staticConfig'))
