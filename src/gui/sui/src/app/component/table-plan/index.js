import TablePlan from './TablePlan'
import withOnTableClick from '../../util/withOnTableClick'
import withStaticConfig from '../../util/withStaticConfig'
import withState from '../../../util/withState'

export default withStaticConfig(withOnTableClick(withState(TablePlan, 'showTableInfo', 'selectedTable', 'theme')))
