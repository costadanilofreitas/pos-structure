import React from 'react'
import PropTypes from 'prop-types'

import { GridContainer } from "./StyledFlexGrid"


export function ensureArray(obj) {
  if (Array.isArray(obj)) {
    return obj
  }
  return [obj]
}

export function insertKey(obj, index) {
  if (React.isValidElement(obj)) {
    return React.cloneElement(obj, {key: index })
  }
  return obj
}

export default function FlexGrid({ direction, children, className, gridRef, onClick }) {
  let outerClass = className === undefined ? '' : className

  return (
    <GridContainer className={outerClass}
         style={{ flexDirection: direction }}
         ref={gridRef}
         onClick={onClick}>
      {ensureArray(children).map((child,  i) => insertKey(child, i))}
    </GridContainer>
  )
}

FlexGrid.defaultProps = {
  direction: 'row'
}

FlexGrid.propTypes = {
  direction: PropTypes.oneOf(['row', 'column', 'row-reverse', 'column-reverse']),
  children: PropTypes.node,
  className: PropTypes.string,
  gridRef: PropTypes.func,
  onClick: PropTypes.func
}
