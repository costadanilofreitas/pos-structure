import PropTypes from 'prop-types'

const OperatorPropTypes = PropTypes.shape({
  id: PropTypes.string,
  name: PropTypes.string,
  state: PropTypes.oneOf(['LOGGEDOUT', 'LOGGEDIN', 'PAUSED', 'OPENED', 'UNDEFINED']),
  stateCode: PropTypes.string,
  sessionId: PropTypes.string,
  initialFloat: PropTypes.string
})

export default OperatorPropTypes
