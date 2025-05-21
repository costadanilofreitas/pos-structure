import ProductGrid from './JssProductGrid'
import withState from '../../../util/withState'

export default withState(ProductGrid, 'staticConfig', 'specialCatalog', 'deviceType')
