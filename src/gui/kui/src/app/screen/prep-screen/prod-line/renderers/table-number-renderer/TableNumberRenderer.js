import React from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'
import LinePropTypes from '../../../../../prop-types/LinePropTypes'
import LineValueColumnPropTypes from '../../../../../prop-types/LineValueColumnPropTypes'

export default function TableNumberRenderer({ line, column }) {
  let value = _.get(line, 'orderData.properties.TAB_ID')
  if (value === undefined) {
    value = _.get(line, 'orderData.properties.TABLE_ID')
  } else {
    value = `C -${value}`
  }

  if (value == null) {
    value = '-'
  }

  return <span style={column.style}>{value}</span>
}

TableNumberRenderer.propTypes = {
  line: LinePropTypes,
  column: LineValueColumnPropTypes,
  classes: PropTypes.object
}
