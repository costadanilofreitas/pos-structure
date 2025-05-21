import TableList from './TableList'
import withOnTableClick from '../../util/withOnTableClick'
import withStaticConfig from '../../util/withStaticConfig'
import withShowTabs from '../../util/withShowTabs'
import withState from '../../../util/withState'

export default withStaticConfig(withOnTableClick(withShowTabs(withState(TableList, 'workingMode'))))
