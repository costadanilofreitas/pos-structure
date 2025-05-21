import TableDetails from './TableDetails'
import withGetCurrentDate from '../../../util/withGetCurrentDate'
import withState from '../../../util/withState'

export default withGetCurrentDate(withState(TableDetails, 'userList'))
