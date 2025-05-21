import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'
import injectSheet, { jss } from 'react-jss'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = (theme) => ({
  dataTableRoot: {
    composes: 'data-table-root',
    width: '100%',
    borderCollapse: 'separate',
    borderSpacing: '0 0.5vmin'
  },
  tableRow: {
    backgroundColor: theme.backgroundColor,
    color: theme.color,
    '&:nth-child(odd)': {
      backgroundColor: theme.titleBackgroundColor
    }
  },
  alertRow: {
    color: theme.recallAlertColor,
    '&:nth-child(odd)': {
      backgroundColor: theme.titleBackgroundColor
    }
  }
})

class DataTable extends PureComponent {
  renderHead = (filteredColumns) => {
    const { styleHeaderRow } = this.props

    return (
      <thead>
        <tr style={styleHeaderRow}>
          {_.map(filteredColumns, (col, idx) => (
            <th key={`h_${idx}`} style={{ ...(col.headerStyle || {}) }}>{col.title}</th>
          ))}
        </tr>
      </thead>
    )
  }

  renderCell = (line, col) => {
    if (col.onRenderCell) {
      return col.onRenderCell(line, col)
    }
    return _.get(line, col.path)
  }

  renderBody = (filteredColumns) => {
    const { data, styleRow, styleCell, classes } = this.props

    return (
      <tbody>
        {_.map(data, (line, idxRow) => (
          <tr key={`r_${idxRow}`} style={styleRow} className={line.isAlert ? classes.alertRow : classes.tableRow}>
            {_.map(filteredColumns, (col, idxCol) => (
              <td
                key={`c_${idxRow}.${idxCol}`}
                style={col.styleCell || styleCell}
                className={col.path}
              >
                {this.renderCell(line, col)}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    )
  }

  render() {
    const { classes, style, className, columns } = this.props
    const filteredColumns = columns.filter(
      function (col) {
        return !col.disabled
      }
    )

    return (
      <table className={`${classes.dataTableRoot} ${className}`} style={style}>
        {this.renderHead(filteredColumns)}
        {this.renderBody(filteredColumns)}
      </table>
    )
  }
}

DataTable.propTypes = {
  classes: PropTypes.object,
  style: PropTypes.object,
  styleHeaderRow: PropTypes.object,
  styleRow: PropTypes.object,
  styleCell: PropTypes.object,
  className: PropTypes.string,
  columns: PropTypes.arrayOf(PropTypes.shape({
    path: PropTypes.string,
    headerStyle: PropTypes.object,
    title: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
    onRenderCell: PropTypes.func,
    disabled: PropTypes.bool
  })),
  data: PropTypes.array
}

DataTable.defaultProps = {
  style: {},
  styleHeaderRow: {},
  styleRow: {},
  styleCell: {},
  className: '',
  columns: [],
  data: []
}

export default injectSheet(styles)(DataTable)
