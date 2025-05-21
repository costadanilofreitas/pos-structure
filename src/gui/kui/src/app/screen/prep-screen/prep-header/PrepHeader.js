import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { I18N } from '3s-posui/core'

import { PrepHeaderRoot, PrepHeaderItem } from './StyledPrepHeader'


export default class PrepHeader extends PureComponent {
  render() {
    const { columns } = this.props

    return (
      <PrepHeaderRoot>
        {columns.map(column => (
          <PrepHeaderItem key={column.id} size={column.size} style={column.style}>
            <I18N id={column.title}/>
          </PrepHeaderItem>
        ))}
      </PrepHeaderRoot>
    )
  }
}

PrepHeader.propTypes = {
  columns: PropTypes.array.isRequired
}

PrepHeader.defaultProps = {
  kdsModel: {},
  name: 'header'
}
