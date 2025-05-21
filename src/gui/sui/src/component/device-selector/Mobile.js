import React from 'react'
import PropTypes from 'prop-types'
import Selector from './Selector'


export default function Mobile({ mobile, children }) {
  return <Selector filter={'mobile'} mobile={mobile}>{children}</Selector>
}

Mobile.propTypes = {
  mobile: PropTypes.bool,
  children: PropTypes.oneOfType([PropTypes.object, PropTypes.array])
}
