import SaleSummaryScreen from './SaleSummaryScreen'
import withExecuteActionMessageBus from '../../../util/withExecuteActionMessageBus'
import withStaticConfig from '../../util/withStaticConfig'
import withState from '../../../util/withState'

export default withStaticConfig(withExecuteActionMessageBus(withState(SaleSummaryScreen, 'order')))
