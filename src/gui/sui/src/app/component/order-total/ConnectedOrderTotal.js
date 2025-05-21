import { connect } from 'react-redux'
import OrderTotal from './OrderTotal'

import withExecuteActionMessageBus from '../../../util/withExecuteActionMessageBus'


function mapStateToProps(state) {
  return {
    order: state.order,
    saleType: state.saleType
  }
}

export default withExecuteActionMessageBus(connect(mapStateToProps)(OrderTotal))
