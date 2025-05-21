import PropTypes from 'prop-types'

const DeviceMessagePropTypes = PropTypes.shape({
  timestamp: PropTypes.number,
  sitef: PropTypes.shape({
    confirmSitef: PropTypes.number
  }),
  printer: PropTypes.shape({
    printData: PropTypes.string
  })
})

export default DeviceMessagePropTypes
