import PropTypes from 'prop-types'

const ColumnPropTypes = PropTypes.shape({
  id: PropTypes.number,
  title: PropTypes.string,
  renderer: PropTypes.string,
  alignment: PropTypes.string,
  size: PropTypes.number
})

export default ColumnPropTypes
