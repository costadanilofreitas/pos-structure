import TableListScreen from './TableListScreen'
import withShowTabs from '../../util/withShowTabs'
import withTables from '../../util/withTables'
import withExecuteActionMessageBus from '../../../util/withExecuteActionMessageBus'
import withState from '../../../util/withState'

const stateListScreen = withState(TableListScreen,
  'floorPlan',
  'showTableInfo')

export default withExecuteActionMessageBus(withShowTabs(withTables(stateListScreen)))
