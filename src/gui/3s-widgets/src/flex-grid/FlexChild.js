import React from 'react'
import PropTypes from 'prop-types'

import { ChildContainer, AbsoluteWrapper } from './StyledFlexGrid'

export default function FlexChild({ size, children, className, style, outerClassName, innerClassName }) {
  const outerClass = outerClassName == null ? '' : outerClassName
  const innerClass = innerClassName == null ? '' : innerClassName

  const childClass = className == null ? innerClass : `${className} ${innerClass}`
  const childStyle = style == null ? '' : style

  return (
    <ChildContainer className={outerClass} style={{ flex: size.toString() }}>
      <AbsoluteWrapper className={childClass} style={{...childStyle}}>
        {children}
      </AbsoluteWrapper>
    </ChildContainer>
  )
}

FlexChild.defaultProps = {
  size: 1
}

FlexChild.propTypes = {
  children: PropTypes.node,
  size: PropTypes.number,
  className: PropTypes.string,
  style: PropTypes.object,
  outerClassName: PropTypes.string,
  innerClassName: PropTypes.string
}
