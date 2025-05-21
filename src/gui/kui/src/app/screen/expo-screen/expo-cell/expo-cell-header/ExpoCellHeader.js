import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { ExpoCellContainer, TitleBlock, OverflowContainer } from './StyledExpoCellHeader'
import parseMacros from '../../../../../util/CellFormater'


export default class ExpoCellHeader extends Component {
  render() {
    const { format, order, selected, borderRadius, timerColor, backgroundColor, blink, theme } = this.props

    return (
      <ExpoCellContainer
        backgroundColor={backgroundColor}
        selected={selected}
        className={'test_KdsCell_HEADER'}
        borderRadius={borderRadius}
        blink={blink}
      >
        <TitleBlock>
          {order.page === 1 &&
            <OverflowContainer>
              {parseMacros(format, order, timerColor, theme)}
            </OverflowContainer>
          }
        </TitleBlock>
      </ExpoCellContainer>
    )
  }
}

ExpoCellHeader.propTypes = {
  order: PropTypes.object,
  format: PropTypes.string,
  selected: PropTypes.bool,
  borderRadius: PropTypes.string,
  timerColor: PropTypes.string,
  backgroundColor: PropTypes.string,
  blink: PropTypes.bool,
  theme: PropTypes.object
}
