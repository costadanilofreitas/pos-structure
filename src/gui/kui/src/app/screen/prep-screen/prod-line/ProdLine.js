import React, { Component } from 'react'
import PropTypes from 'prop-types'

import LineValueRenderer from './renderers/line-value-renderer'
import LineAgeRenderer from './renderers/line-age-renderer'
import LineItemsRenderer from './renderers/line-items-renderer'

import LinePropTypes from '../../../prop-types/LinePropTypes'
import ColumnPropTypes from '../../../prop-types/ColumnPropTypes'
import KdsModelPropTypes from '../../../prop-types/KdsModelPropTypes'
import LineCookTimeRenderer from './renderers/line-cook-time-renderer'
import TableNumberRenderer from './renderers/table-number-renderer'
import LineSaleTypeRenderer from './renderers/line-sale-type-renderer'
import LineActionsRenderer from './renderers/line-actions-renderer'
import { shallowIgnoreEquals } from '../../../../util/renderUtil'

import { Container, ContentContainer } from './StyledProdLine'

export default class ProdLine extends Component {
  constructor(props) {
    super(props)

    this.renderers = {
      'LineValueRenderer': LineValueRenderer,
      'LineAgeRenderer': LineAgeRenderer,
      'LineItemsRenderer': LineItemsRenderer,
      'LineCookTimeRenderer': LineCookTimeRenderer,
      'TableNumberRenderer': TableNumberRenderer,
      'LineSaleTypeRenderer': LineSaleTypeRenderer,
      'LineActionsRenderer': LineActionsRenderer
    }

    this.state = {
      selected: props.currentLine === props.rowIndex
    }
  }

  render() {
    const { line, rowIndex, columns, zoom, selectLine, minHeight } = this.props
    const handleSelectLine = () => selectLine(rowIndex)

    let currentFontSize = 1.5 + (0.5 * zoom)
    currentFontSize += 'vmin'

    const threshold = this.getCurrentThreshold(line)

    return (
      <Container
        reference={this.handleReference}
        selected={this.state.selected}
        threshold={threshold}
        onClick={handleSelectLine}
        className={`test_Line_CONTAINER threshold_${threshold}`}
        style={{ minHeight }}
      >
        {columns.map((column, colIndex) => (
          <ContentContainer
            width={column.size}
            key={`${rowIndex}.${colIndex}`}
            fontSize={currentFontSize}
          >
            {React.createElement(
              this.renderers[column.renderer],
              {
                line: line,
                rowIndex: rowIndex,
                colIndex: colIndex,
                column: column,
                currentThreshold: threshold
              })}
          </ContentContainer>
        ))}
      </Container>
    )
  }

  static getDerivedStateFromProps(nextProps) {
    return {
      selected: nextProps.currentLine === nextProps.rowIndex
    }
  }

  shouldComponentUpdate(nextProps, nextState) {
    const isEqual = shallowIgnoreEquals(
      this.props,
      nextProps,
      'currentLine',
      'kdsModel',
      'reference')

    if (!isEqual) {
      return true
    }

    if ((this.props.currentLine !== this.props.rowIndex &&
        nextProps.currentLine !== nextProps.rowIndex) ||
        (this.props.currentLine === this.props.rowIndex &&
         nextProps.currentLine === nextProps.rowIndex)) {
      return false
    }

    return (
      nextState.selected !== this.state.selected
      || nextProps.line !== this.props.line
      || nextProps.zoom !== this.zoom
    )
  }

  handleReference = (ref) => {
    if (this.props.reference != null) {
      this.props.reference(this.props.rowIndex, ref)
    }
  }

  getCurrentThreshold = (line) => {
    const { thresholds, viewWithActions } = this.props.kdsModel
    if (!viewWithActions) {
      return 0
    }

    let elapsed = (new Date() - line.orderData.attributes.displayTime) + this.props.timeDelta
    elapsed /= 1000
    for (let i = thresholds.length - 1; i >= 0; i--) {
      if (elapsed > parseFloat(thresholds[i].time)) {
        return i + 1
      }
    }
    return 0
  }
}

ProdLine.propTypes = {
  line: LinePropTypes,
  currentLine: PropTypes.number,
  columns: PropTypes.arrayOf(ColumnPropTypes),
  rowIndex: PropTypes.number,
  zoom: PropTypes.number,
  kdsModel: KdsModelPropTypes,
  reference: PropTypes.func,
  timeDelta: PropTypes.number,
  selectLine: PropTypes.func,
  minHeight: PropTypes.string
}
