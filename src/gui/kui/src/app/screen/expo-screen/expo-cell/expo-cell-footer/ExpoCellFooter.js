import React, { Component } from 'react'
import PropTypes from 'prop-types'

import parseMacros from '../../../../../util/CellFormater'
import { ExpoCellFooterContainer, OverflowContainer } from './StyledExpoCellFooter'


export default class ExpoCellFooter extends Component {
  render() {
    const { format, order, selected, borderRadius, backgroundColor, blink } = this.props
    return (
      <ExpoCellFooterContainer
        selected={selected}
        className={'test_KdsCell_FOOTER'}
        borderRadius={borderRadius}
        backgroundColor={backgroundColor}
        blink={blink}
      >
        {order.page === order.pages &&
          <OverflowContainer>
            {parseMacros(format, order)}
          </OverflowContainer>
        }
      </ExpoCellFooterContainer>
    )
  }
}

ExpoCellFooter.propTypes = {
  order: PropTypes.object,
  format: PropTypes.string,
  selected: PropTypes.bool,
  borderRadius: PropTypes.string,
  backgroundColor: PropTypes.string,
  blink: PropTypes.bool
}
