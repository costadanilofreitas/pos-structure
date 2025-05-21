import { connect } from 'react-redux'
import RendererChooser from './RendererChooser'


function mapStateToProps(state) {
  return {
    deviceType: state.deviceType
  }
}

export default connect(mapStateToProps)(RendererChooser)
