import DeliveryAddressDialog from './DeliveryAddressDialog'
import withExecuteActionMessageBus from '../../../util/withExecuteActionMessageBus'
import withState from '../../../util/withState'


export default withExecuteActionMessageBus(withState(DeliveryAddressDialog, 'order'))
