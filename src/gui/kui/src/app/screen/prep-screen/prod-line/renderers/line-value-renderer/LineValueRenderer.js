import React from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'
import LinePropTypes from '../../../../../prop-types/LinePropTypes'
import LineValueColumnPropTypes from '../../../../../prop-types/LineValueColumnPropTypes'

export default function LineValueRenderer({ line, column }) {
  let value = _.get(line, column.path)
  if (value == null) {
    value = ''
  } else {
    value %= 10000
  }

  return <span style={column.style}>{value}</span>
}

LineValueRenderer.propTypes = {
  line: LinePropTypes,
  column: LineValueColumnPropTypes,
  classes: PropTypes.object
}
