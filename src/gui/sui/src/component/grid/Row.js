import React from 'react'
import PropTypes from 'prop-types'
import { ensureArray } from '3s-posui/utils'

export default function Row(props) {
  let { children, classes, fluid } = props
  children = ensureArray(children)

  let xsSum = 0
  let rowClass = fluid ? '' : classes.row
  let rowStyle = fluid ? { display: 'flex', width: '100%', height: '100%', alignItems: 'center' } : ''
  if (props.rowSpace != null) {
    rowStyle = Object.assign(rowStyle, { marginBottom: props.rowSpace })
  }

  if (props.className != null) {
    rowClass += ` ${props.className}`
  }
  return (
    <div className={rowClass} style={rowStyle}>
      {children.map((col, idx) => {
        const isFirst = xsSum === 0
        xsSum += col.props.xs
        const isLast = xsSum === 12
        return React.cloneElement(col, { key: idx, isLast: isLast, isFirst: isFirst })
      })}
    </div>
  )
}

Row.propTypes = {
  children: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
  classes: PropTypes.object,
  fluid: PropTypes.bool,
  rowSpace: PropTypes.string,
  className: PropTypes.string
}
