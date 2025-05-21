import MainScreen from './MainScreen'
import withState from '../../../util/withState'

export default withState(MainScreen, 'consolidatedItems', 'kdsModel', 'theme', 'viewsOrders')
