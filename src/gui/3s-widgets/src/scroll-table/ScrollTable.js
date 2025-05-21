import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { jss } from 'react-jss'
import { Table } from 'react-virtualized'
import { debounce } from 'lodash'

import { FlexGrid, FlexChild } from "../flex-grid"

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

class ScrollTable extends PureComponent {
  constructor(props, context) {
    super(props, context)

    this.mainContainer = null

    this.state = {
      scrollToIndex: 0,
      scrollToAlignment: 'start',
      firstVisibleRow: 0,
      lastVisibleRow: 0,
      mainDimensions: null
    }

    this.onScroll = this.onScroll.bind(this)
    this.scrollDiv = this.scrollDiv.bind(this)
  }

  render() {
    const { classes, tableFlex } = this.props
    const { mainDimensions } = this.state

    return (
      <FlexGrid className={classes.scrollTable} direction={'column'}>
        <FlexChild size={tableFlex}>
          <div className={classes.tableContainer} ref={el => (this.mainContainer = el)}>
            { mainDimensions && this.renderContent() }
          </div>
        </FlexChild>
        {this.renderButtons()}
      </FlexGrid>
    )
  }

  componentDidUpdate() {
    if (this.state.mainDimensions != null) {
      let size = this.state.mainDimensions
      if (size.width === this.mainContainer.offsetWidth && size.height === this.mainContainer.offsetHeight) {
        return
      }
    }

    this.setCurrentDimension()
  }

  componentDidMount() {
    this.setCurrentDimension()

    window.addEventListener(
      'resize',
      debounce(() => {
        this.setCurrentDimension()
      }, 200)
    )
  }

  setCurrentDimension() {
    this.setState({
      mainDimensions: {
        width: this.mainContainer.offsetWidth,
        height: this.mainContainer.offsetHeight
      }
    })
  }

  renderContent() {
    const { classes, data, columns, rowsQuantity, overscanRowCount } = this.props
    const { scrollToIndex, scrollToAlignment, mainDimensions } = this.state

    let tableHeight = mainDimensions.height / rowsQuantity
    const rowStyle = {
      paddingRight: '0',
      borderBottom: '1px solid #d7d7d7',
      textAlign: 'center',
      display: 'flex',
      alignItems: 'center',
      maxWidth: '98%',
      padding: ' 0 1%'
    }

    return (
      <Table
        className={classes.table}
        width={mainDimensions.width}
        height={mainDimensions.height}
        headerHeight={tableHeight}
        rowHeight={tableHeight}
        rowCount={data.length}
        rowGetter={({ index }) => data[index]}
        rowStyle={rowStyle}
        overscanRowCount={overscanRowCount}
        onRowsRendered={this.onScroll}
        scrollToIndex={scrollToIndex}
        scrollToAlignment={scrollToAlignment}
      >
        {columns.map((col) => col)}
      </Table>
    )
  }

  renderButtons() {
    const { classes, data, buttonsFlex } = this.props
    const { firstVisibleRow, lastVisibleRow } = this.state

    const upDisabled = firstVisibleRow === 0
    const downDisabled = lastVisibleRow === data.length - 1

    return (
      <FlexChild size={buttonsFlex} outerClassName={classes.scrollButtonsContainer}>
        <FlexGrid direction={'row'}>
          <FlexChild>
            <button
              className={upDisabled
                ? classes.scrollButton + ' ' + classes.scrollButtonDisabled
                : classes.scrollButton}
              onClick={() => this.scrollDiv('up')}>
              <i className="fas fa-caret-up fa-2x" />
            </button>
          </FlexChild>
          <FlexChild>
            <button
              className={downDisabled
                ? classes.scrollButton + ' ' + classes.scrollButtonDisabled
                : classes.scrollButton}
              style={{ borderLeft: '1px solid #d7d7d7' }}
              onClick={() => this.scrollDiv('down')}>
              <i className="fas fa-caret-down fa-2x test_ScrollTable_DOWN" />
            </button>
          </FlexChild>
        </FlexGrid>
      </FlexChild>
    )
  }

  onScroll(rowsRendereds) {
    this.setState({
      firstVisibleRow: rowsRendereds.startIndex,
      lastVisibleRow: rowsRendereds.stopIndex
    })
  }

  scrollDiv(direction) {
    if (direction === 'down') {
      this.setState({ scrollToIndex: this.state.lastVisibleRow, scrollToAlignment: 'start' })
    } else {
      this.setState({ scrollToIndex: this.state.firstVisibleRow, scrollToAlignment: 'end' })
    }
  }
}

ScrollTable.propTypes = {
  classes: PropTypes.object,
  data: PropTypes.array,
  columns: PropTypes.array,
  rowsQuantity: PropTypes.number,
  overscanRowCount: PropTypes.number,
  tableFlex: PropTypes.number,
  buttonsFlex: PropTypes.number
}

ScrollTable.defaultProps = {
  data: [],
  columns: [],
  rowsQuantity: 10,
  overscanRowCount: 5,
  tableFlex: 20,
  buttonsFlex: 1
}

export default ScrollTable
