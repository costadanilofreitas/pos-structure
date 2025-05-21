import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'

import SaleType from './SaleType'
import withExecuteActionMessageBus from '../../../util/withExecuteActionMessageBus'
import { changeSaleType } from '../../../ducks/saleType'
import withState from '../../../util/withState'
import withStaticConfig from '../../util/withStaticConfig'


function mapDispatchToProps(dispatch) {
  return bindActionCreators({
    changeSaleType: changeSaleType
  }, dispatch)
}


export default withStaticConfig(withExecuteActionMessageBus(
  connect(null, mapDispatchToProps)(withState(SaleType, 'order', 'saleType', 'screenOrientation'))))
