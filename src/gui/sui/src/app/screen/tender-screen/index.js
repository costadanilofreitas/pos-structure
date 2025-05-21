import TenderScreen from './TenderScreen'
import withState from '../../../util/withState'
import withExecuteActionMessageBus from '../../../util/withExecuteActionMessageBus'

export default withExecuteActionMessageBus(withState(
  TenderScreen,
  'selectedTable',
  'mobile',
  'tefAvailable',
  'staticConfig',
  'order'))
