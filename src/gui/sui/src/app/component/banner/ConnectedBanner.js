import Banner from './Banner'
import withState from '../../../util/withState'
import withExecuteActionMessageBus from '../../../util/withExecuteActionMessageBus'

export default withExecuteActionMessageBus(withState(Banner, 'staticConfig', 'order', 'saleType'))
