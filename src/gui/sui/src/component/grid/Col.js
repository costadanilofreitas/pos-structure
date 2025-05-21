import React from 'react'
import PropTypes from 'prop-types'

export default function Col({ children, xs, isLast, isFirst, classes }) {
  const className = `xs${xs}`
  let innerClassName = classes.colInner
  if (isLast) {
    innerClassName += ` ${classes.lastColInner}`
  }
  if (isFirst) {
    innerClassName += ` ${classes.firstColInner}`
  }
  return <div className={`${classes[className]} ${classes.col}`}><div className={innerClassName}>{children}</div></div>
}

Col.propTypes = {
  children: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
  xs: PropTypes.number,
  isLast: PropTypes.bool,
  isFirst: PropTypes.bool,
  classes: PropTypes.object
}
