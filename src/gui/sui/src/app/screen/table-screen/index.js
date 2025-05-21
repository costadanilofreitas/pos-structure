import { connect } from 'react-redux'

import TableScreen from './TableScreen'

function mapStateToProps(state) {
  return {
    selectedTable: state.selectedTable,
    showTableInfo: state.showTableInfo
  }
}

export default connect(mapStateToProps)(TableScreen)
