import PropTypes from 'prop-types'

const OrderDataPropTypes = PropTypes.shape({
  attributes: PropTypes.shape({
    id: PropTypes.number,
    prodState: PropTypes.string,
    displayTime: PropTypes.instanceOf(Date)
  }),
  properties: PropTypes.shape({
    TABLE_ID: PropTypes.string
  })
})

export default OrderDataPropTypes
