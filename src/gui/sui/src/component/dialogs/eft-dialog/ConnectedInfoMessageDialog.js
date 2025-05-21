import { connect } from 'react-redux'

import InfoMessageDialog from './InfoMessageDialog'

function mapStateToProps(state) {
  return {
    infoMessage: state.infoMessage
  }
}

export default connect(mapStateToProps)(InfoMessageDialog)
