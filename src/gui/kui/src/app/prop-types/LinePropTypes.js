import PropTypes from 'prop-types'
import OrderDataPropTypes from './OrderDataPropTypes'

const LinePropTypes = PropTypes.shape({
  orderData: OrderDataPropTypes,
  items: PropTypes.array
})

export default LinePropTypes
