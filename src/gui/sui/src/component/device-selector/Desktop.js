import React from 'react'
import PropTypes from 'prop-types'

import Selector from './Selector'


export default function Desktop({ mobile, children }) {
  return <Selector filter={'desktop'} mobile={mobile}>{children}</Selector>
}

Desktop.propTypes = {
  mobile: PropTypes.bool,
  children: PropTypes.oneOfType([PropTypes.object, PropTypes.array])
}
