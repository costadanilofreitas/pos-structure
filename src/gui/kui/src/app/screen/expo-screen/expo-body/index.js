import withState from '../../../../util/withState'
import ExpoBody from './ExpoBody'


export default withState(ExpoBody, 'kdsModel', 'timeDelta', 'currentOrder', 'paginationBlockSize')
