import React from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'

import { I18N } from '3s-posui/core'

import LinePropTypes from '../../../../../prop-types/LinePropTypes'
import LineValueColumnPropTypes from '../../../../../prop-types/LineValueColumnPropTypes'

export default function LineSaleTypeRenderer({ line, column }) {
  const value = `$${_.get(line, 'orderData.attributes.saleType')}`
  return <span style={column.style}><I18N id={value}/></span>
}

LineSaleTypeRenderer.propTypes = {
  line: LinePropTypes,
  column: LineValueColumnPropTypes,
  classes: PropTypes.object
}
