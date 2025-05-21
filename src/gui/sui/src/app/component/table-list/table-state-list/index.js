import { connect } from 'react-redux'

import TableStateList from './JssTableStateList'

function mapStateToProps(state) {
  return {
    operator: state.operator
  }
}

export default connect(mapStateToProps)(TableStateList)

