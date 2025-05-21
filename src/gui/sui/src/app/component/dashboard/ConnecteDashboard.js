import withStaticConfig from '../../util/withStaticConfig'
import Dashboard from './Dashboard'
import withState from '../../../util/withState'

export default withStaticConfig(withState(Dashboard, 'tableLists', 'floorPlan'))
