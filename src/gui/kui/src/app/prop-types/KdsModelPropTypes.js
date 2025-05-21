import PropTypes from 'prop-types'

const KdsModelPropTypes = PropTypes.shape({
  id: PropTypes.number,
  title: PropTypes.string,
  layout: PropTypes.shape({
    lines: PropTypes.number
  })
})

export default KdsModelPropTypes
