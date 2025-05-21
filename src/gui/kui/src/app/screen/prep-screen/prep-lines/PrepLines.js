import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { ScrollPanel, FlexChild, FlexGrid } from '3s-widgets'

import LinePropTypes from '../../../prop-types/LinePropTypes'
import ColumnPropTypes from '../../../prop-types/ColumnPropTypes'
import KdsModelPropTypes from '../../../prop-types/KdsModelPropTypes'
import { shallowIgnoreEquals } from '../../../../util/renderUtil'
import ProdLine from '../prod-line'
import PrepHeader from '../prep-header'
import { PrepBody } from './StyledPrepLines'


export default class PrepLines extends Component {
  constructor(props) {
    super(props)
    this.scrollPanel = null
    this.linesRef = {}
    this.defaultShorterThresHold = 999999999

    this.state = {
      redraw: false,
      lineChanged: true,
      zoomChanged: false,
      lastZoom: props.zoom,
      currentLine: props.currentLine
    }

    this.handleLineReference = this.handleLineReference.bind(this)
    this.redraw = this.redraw.bind(this)
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    const lineChanged = nextProps.currentLine !== prevState.currentLine || nextProps.zoom !== prevState.lastZoom
    return {
      ...prevState,
      lineChanged: prevState.lineChanged !== true ? lineChanged : true,
      zoomChanged: prevState.zoomChanged !== true ? nextProps.zoom !== prevState.lastZoom : true,
      lastZoom: nextProps.zoom,
      currentLine: nextProps.currentLine
    }
  }

  shouldComponentUpdate(nextProps, nextState) {
    if (nextState.lineChanged) {
      return true
    }

    return !shallowIgnoreEquals(
      this.props,
      nextProps,
      'currentLine',
      'kdsModel')
  }

  render() {
    const { columns, kdsModel, lines } = this.props
    const { redraw } = this.state
    const minHeightPerLine = `calc(${Math.round(100 / (kdsModel.layout.lines || 4))}% - ${
      Math.round(4 / (kdsModel.layout.lines || 4))}vh)`

    return (
      <FlexGrid direction={'column'}>
        <FlexChild>
          <PrepHeader columns={columns}/>
        </FlexChild>
        <FlexChild size={19}>
          <PrepBody>
            <ScrollPanel reference={(el) => {
              this.scrollPanel = el
            }}>
              {lines.map((line, rowIndex) => (
                <ProdLine
                  key={rowIndex}
                  line={line}
                  rowIndex={rowIndex}
                  columns={columns}
                  reference={this.handleLineReference}
                  redraw={redraw}
                  minHeight={minHeightPerLine}
                />
              ))}
            </ScrollPanel>
          </PrepBody>
        </FlexChild>
      </FlexGrid>
    )
  }

  componentDidUpdate() {
    const shorterThreshold = this.getShorterThreshold(this.props.lines)
    const redrawFunction = this.redraw

    if (this.state.zoomChanged === true) {
      setTimeout(redrawFunction, 250)
      this.setState({
        zoomChanged: false
      })
    } else if (this.state.lineChanged === true) {
      if (this.scrollPanel != null && this.linesRef[this.props.currentLine] != null) {
        this.scrollPanel.ensureVisible(this.linesRef[this.props.currentLine])

        this.setState({
          lineChanged: false
        })
      }
    }

    if (shorterThreshold !== this.defaultShorterThresHold) {
      setTimeout(redrawFunction, shorterThreshold)
    }
  }

  redraw() {
    const { redraw } = this.state
    const currentRedraw = !redraw
    this.setState({ redraw: currentRedraw })
  }

  handleLineReference(index, ref) {
    this.linesRef[index] = ref
  }

  getShorterThreshold(filteredDisplayLines) {
    const { thresholds } = this.props.kdsModel
    let shorterThresHold = this.defaultShorterThresHold
    for (let i = 0; i < filteredDisplayLines.length; i++) {
      const elapsed = (new Date() - filteredDisplayLines[0].orderData.attributes.displayTime) + this.props.timeDelta
      for (let j = thresholds.length - 1; j >= 0; j--) {
        const threshold = parseFloat(thresholds[j].time)
        const currentShorterThresHold = threshold - elapsed
        if (threshold > elapsed && currentShorterThresHold < shorterThresHold) {
          shorterThresHold = currentShorterThresHold
        }
      }
    }

    return shorterThresHold
  }
}

PrepLines.propTypes = {
  lines: PropTypes.arrayOf(LinePropTypes),
  rows: PropTypes.number,
  columns: PropTypes.arrayOf(ColumnPropTypes),
  currentLine: PropTypes.number,
  kdsModel: KdsModelPropTypes,
  zoom: PropTypes.number,
  timeDelta: PropTypes.number
}
