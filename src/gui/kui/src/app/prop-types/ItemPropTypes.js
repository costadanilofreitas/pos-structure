import PropTypes from 'prop-types'

const ItemPropTypes = PropTypes.shape({
  lineNumber: PropTypes.number,
  itemId: PropTypes.string,
  partCode: PropTypes.number,
  level: PropTypes.number,
  qty: PropTypes.number,
  description: PropTypes.string,
  items: PropTypes.array,
  tags: PropTypes.array,
  tagHistory: PropTypes.array
})

export default ItemPropTypes
