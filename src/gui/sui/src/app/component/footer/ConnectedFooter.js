import Footer from './Footer'
import withState from '../../../util/withState'
import withExecuteActionMessageBus from '../../../util/withExecuteActionMessageBus'

export default withExecuteActionMessageBus(withState(Footer, 'order', 'staticConfig'))
