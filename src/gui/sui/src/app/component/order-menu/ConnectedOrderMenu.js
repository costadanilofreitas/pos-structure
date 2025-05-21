import { connect } from 'react-redux'
import OrderMenu from './JssOrderMenu'
import withState from '../../../util/withState'

function mapStateToProps({ custom }) {
  return { custom, themeName: (custom || {}).THEME || 'default' }
}

export default connect(mapStateToProps)(withState(OrderMenu, 'deviceType'))
