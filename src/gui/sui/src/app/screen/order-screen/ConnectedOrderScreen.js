import OrderScreen from './OrderScreen'
import withState from '../../../util/withState'

export default withState(OrderScreen,
  'actionRunning',
  'order',
  'mobile',
  'workingMode',
  'navigation',
  'saleType',
  'staticConfig',
  'specialCatalog',
  'orderLastTimestamp',
  'modifiers',
  'selectedTable',
  'deviceType',
  'screenOrientation',
  'products')
