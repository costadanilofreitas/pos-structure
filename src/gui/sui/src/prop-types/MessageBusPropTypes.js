import PropTypes from 'prop-types'

const MessageBusPropTypes = PropTypes.shape({
  syncAction: PropTypes.func.isRequired,
  parallelSyncAction: PropTypes.func
})

export default MessageBusPropTypes
