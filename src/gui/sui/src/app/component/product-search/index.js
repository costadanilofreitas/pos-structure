import ProductSearch from './ProductSearch'
import withState from '../../../util/withState'

export default withState(ProductSearch, 'posId', 'products')
