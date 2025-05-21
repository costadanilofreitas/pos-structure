import React, {Component} from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'

import {ScrollPanel} from '3s-widgets'
import {compareProps} from '3s-posui/utils'
import injectSheet, {jss} from 'react-jss'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = {
  buttonGridRoot: {
    composes: 'button-grid-root',
    position: 'absolute',
    display: 'flex',
    flexWrap: 'wrap',
    height: '100%',
    width: '100%'
  },
  buttonGridWithTitleRoot: {
    composes: 'button-grid-with-title-root',
    position: 'absolute',
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    width: '100%'
  },
  buttonGridRootWrapper: {
    composes: 'button-grid-root-wrapper',
    position: 'relative',
    flexGrow: 1,
    flexBasis: '0%'
  },
  buttonGridTitleRoot: {
    composes: 'button-grid-title-root'
  },
  buttonGridTitle: {
    composes: 'button-grid-title',
    width: '100%',
    fontSize: '1.8vmin',
    padding: '1vh 0',
    textAlign: 'center'
  },
  buttonGridCellRoot: {
    composes: 'button-grid-cell-root',
    position: 'relative',
    boxSizing: 'border-box'
  }
}

const getCalcStyles = (props) => {
  const {
    classes, style, styleTitleRoot, styleTitle, styleCell, title, rows, cols, direction, visibleRows,
    titleDescription, styleTitleDescription
  } = props
  let titleRow = null
  if (title) {
    const isString = typeof title === 'string' || title instanceof String
    titleRow = (
      <div className={classes.buttonGridTitleRoot} style={styleTitleRoot}>
        {isString ?
          <div className={classes.buttonGridTitle} style={styleTitle}>
            {title}
            {titleDescription &&
            <div style={styleTitleDescription}>{titleDescription}</div>
            }
          </div> : title
        }
      </div>
    )
  }
  let flexBasis
  let height
  let width
  const actualRows = (!visibleRows) ? rows : visibleRows
  if (direction === 'row') {
    flexBasis = `${100 / cols}%`
    height = `${100 / actualRows}%`
    width = flexBasis
  } else {
    flexBasis = `${100 / actualRows}%`
    height = flexBasis
    width = `${100 / cols}%`
  }

  const gridContentStyle = { ...style, flexDirection: direction }
  const cellStyle = { flexBasis, width, maxWidth: width, ...styleCell, height }

  return { titleRow, gridContentStyle, cellStyle }
}

class ButtonGrid extends Component {
  constructor(props) {
    super(props)
    this.state = {
      calcStyles: getCalcStyles(props)
    }
  }

  static getDerivedStateFromProps(props, state) {
    if (state.style !== props.style ||
      state.styleTitleRoot !== props.styleTitleRoot ||
      state.styleTitle !== props.styleTitle ||
      state.styleCell !== props.styleCell ||
      state.title !== props.title ||
      state.rows !== props.rows ||
      state.cols !== props.cols ||
      state.direction !== props.direction ||
      state.visibleRows !== props.visibleRows) {
      return { calcStyles: getCalcStyles(props) }
    }
    return {}
  }

  shouldComponentUpdate(nextProps, nextState) {
    return compareProps(this.props, this.state, nextProps, nextState, ['buttons'])
  }

  render() {
    const { classes, buttons, className, rows, cols, styleButtonGrid, renderWithScrollPanel } = this.props
    const quantityButtons = Object.keys(buttons).length > rows * cols ? Object.keys(buttons).length : rows * cols
    const gridContent = this.getGridContent(classes, className, quantityButtons, buttons, renderWithScrollPanel)
    if (!this.state.calcStyles.titleRow) {
      return gridContent
    }
    return (
      <div className={classes.buttonGridWithTitleRoot} style={styleButtonGrid}>
        {this.state.calcStyles.titleRow}
        <div className={classes.buttonGridRootWrapper}>
          {gridContent}
        </div>
      </div>
    )
  }

  getGridContent(classes, className, quantityButtons, buttons, renderWithScrollPanel) {
    return (
      <div className={`${classes.buttonGridRoot} ${className}`} style={this.state.calcStyles.gridContentStyle}>
        {this.renderScrollPanel(quantityButtons, classes, buttons, renderWithScrollPanel)}
      </div>
    )
  }

  renderScrollPanel(quantityButtons, classes, buttons, renderWithScrollPanel) {
    if (renderWithScrollPanel) {
      return (
        <ScrollPanel styleCont={{ display: 'flex', flexDirection: 'row', flexWrap: 'wrap' }}>
          {this.getGridButtons(quantityButtons, classes, buttons)}
        </ScrollPanel>
      )
    }

    return <>{this.getGridButtons(quantityButtons, classes, buttons)}</>
  }

  getGridButtons(quantityButtons, classes, buttons) {
    return <>
      {_.map(_.range(quantityButtons), (idx) => {
        return (
          <div key={`cell_${idx}`} className={classes.buttonGridCellRoot} style={this.state.calcStyles.cellStyle}>
            {buttons[idx]}
          </div>
        )
      })}
    </>
  }
}

ButtonGrid.propTypes = {
  classes: PropTypes.object,
  style: PropTypes.object,
  styleButtonGrid: PropTypes.object,
  styleTitleRoot: PropTypes.object,
  styleTitle: PropTypes.object,
  styleCell: PropTypes.object,
  className: PropTypes.string,
  direction: PropTypes.oneOf(['row', 'column']),
  title: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  titleDescription: PropTypes.string,
  buttons: PropTypes.object.isRequired,
  cols: PropTypes.number.isRequired,
  rows: PropTypes.number.isRequired,
  visibleRows: PropTypes.number,
  styleTitleDescription: PropTypes.object,
  renderWithScrollPanel: PropTypes.bool
}

ButtonGrid.defaultProps = {
  style: {},
  styleButtonGrid: {},
  styleTitle: {},
  styleTitleRoot: {},
  styleCell: {},
  className: '',
  direction: 'row',
  title: null,
  titleDescription: null,
  styleTitleDescription: {},
  renderWithScrollPanel: false
}

export default injectSheet(styles)(ButtonGrid)
