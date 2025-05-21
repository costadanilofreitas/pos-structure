import React, { Component } from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'
import { Button } from '3s-posui/button'
import GroupsRenderer from './GroupsRenderer'

class DesktopNavigationGridRenderer extends Component {
  constructor(props) {
    super(props)

    this.getNecessaryRows = this.getNecessaryRows.bind(this)
  }

  render() {
    const { groups = [], rows, cols, expandCol } = this.props
    const totalButtonsPerGroup = _.map(groups, (group) => (group.items || []).length)
    const colsNeededByGroup = _.map(totalButtonsPerGroup, (total) => Math.ceil(total / rows))
    let remainingCols = cols
    const expandColDef = expandCol || cols
    const renderedGoups = _.map(groups, (group, idx) => {
      remainingCols -= colsNeededByGroup[idx]
      return (
        <GroupsRenderer
          {...this.props}
          groups={[group]}
          index={idx}
          key={idx}
          styleOuter={{
            position: 'relative',
            flexGrow: this.getNecessaryRows([group], cols),
            flexBasis: 0,
            flexShrink: 0
          }}
          getNecessaryRows={this.getNecessaryRows}
          cols={colsNeededByGroup[idx]}
        />
      )
    })
    this.appendRemainingCols(renderedGoups, remainingCols, cols, expandColDef)
    return this.renderWithSeparators(renderedGoups)
  }

  getButtonsForGrid(group, idx) {
    const { enabled, sellFunc, onRenderSaleButton, buttonProps } = this.props
    const items = group.items || []
    const groupName = group.name || group.text
    const disabled = !enabled
    const buttons = _.zipObject(
      _.range(items.length),
      _.map(items, (item, buttonIdx) => {
        const key = `${idx}.${groupName}.${buttonIdx}.${disabled}`
        if (onRenderSaleButton) {
          return onRenderSaleButton(item, key, sellFunc, enabled)
        }
        return (
          <Button
            key={key}
            className="navigation-grid-button"
            classNamePressed="navigation-grid-button-pressed"
            disabled={item.disabled || disabled}
            style={{ backgroundColor: item.bgColor }}
            executeAction={() => sellFunc(item)}
            {...buttonProps}
          >
            {item.text}
          </Button>
        )
      })
    )
    return buttons
  }

  appendRemainingCols(renderedGroups, remainingCols, numCols, expandCol) {
    let remaining = remainingCols
    if (numCols - remaining <= expandCol) {
      remaining -= (numCols - expandCol)
    }
    while (remaining > 0) {
      renderedGroups.push(
        <div
          key={`spacer_${remaining}`}
          style={{
            flexGrow: 1,
            flexBasis: 0,
            flexShrink: 0
          }}
        />
      )
      remaining--
    }
  }

  renderWithSeparators(renderedGoups) {
    const { classes, cols, className } = this.props
    const grow = 0.5 / cols
    return (
      <div className={`${classes.navigationGridFlexCont} ${className}`}>
        {_.flatMap(renderedGoups, (value, idx, array) =>
          (array.length - 1 !== idx)
            ? [
              value,
              <div
                key={`group_sep_${idx}`}
                style={{
                  flexGrow: grow,
                  flexBasis: 0,
                  flexShrink: 0
                }}
              />
            ] : value
        )
        }
      </div>
    )
  }

  getNecessaryRows(filteredGroups, cols) {
    const { rows } = this.props
    const numGroups = filteredGroups.length
    let rowsNeeded = []
    if (numGroups > 1) {
      let remainingRows = rows
      rowsNeeded = _.map(filteredGroups, (group, idxGroup) => {
        if (idxGroup === numGroups - 1) {
          return remainingRows
        }
        const needed = Math.ceil((group.items || []).length / cols)
        remainingRows -= needed
        return needed
      })
    } else {
      rowsNeeded.push(rows)
    }

    return rowsNeeded
  }
}

DesktopNavigationGridRenderer.propTypes = {
  classes: PropTypes.object,
  style: PropTypes.object,
  styleTitle: PropTypes.object,
  className: PropTypes.string,
  groups: PropTypes.array.isRequired,
  cols: PropTypes.number,
  rows: PropTypes.number,
  expandCol: PropTypes.number,
  groupsPerCol: PropTypes.number,
  maxSpanCols: PropTypes.number,
  sellFunc: PropTypes.func,
  enabled: PropTypes.bool,
  onRenderSaleButton: PropTypes.func,
  filterClass: PropTypes.string,
  buttonProps: PropTypes.object,
  groupHints: PropTypes.array,
  showTitle: PropTypes.bool
}

DesktopNavigationGridRenderer.defaultProps = {
  style: {},
  styleTitle: {},
  className: '',
  cols: 7,
  rows: 7,
  expandCol: 6,
  groupsPerCol: 2,
  maxSpanCols: 3,
  sellFunc: (item) => ['doSale', item.product_code, 1],
  enabled: true,
  buttonProps: {},
  showTitle: true
}

export default (DesktopNavigationGridRenderer)
