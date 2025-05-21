import React from 'react'
import PropTypes from 'prop-types'


export default function Selector({ filter, mobile, children }) {
  if ((filter === 'mobile' && mobile === true) || (filter === 'desktop' && mobile !== true)) {
    if (Array.isArray(children)) {
      return <div>{children.map(child => child)}</div>
    }
    return children
  }

  return <div/>
}

Selector.propTypes = {
  mobile: PropTypes.bool,
  filter: PropTypes.string,
  children: PropTypes.oneOfType([PropTypes.object, PropTypes.array])
}
