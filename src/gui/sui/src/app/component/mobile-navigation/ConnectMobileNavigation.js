import MobileNavigation from './MobileNavigation'
import withState from '../../../util/withState'


export default withState(
  MobileNavigation,
  'navigation',
  'staticConfig',
  'specialCatalog',
  'selectedTable')
