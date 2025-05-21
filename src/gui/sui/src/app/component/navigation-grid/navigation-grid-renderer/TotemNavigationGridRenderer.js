import React, { Component } from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'

import GroupsRenderer from './GroupsRenderer'


class TotemNavigationGridRenderer extends Component {
  constructor(props) {
    super(props)

    this.getNecessaryRows = this.getNecessaryRows.bind(this)
  }

  render() {
    const { groups, rows, cols, maxSpanCols, expandCol } = this.props
    let remainingCols = cols
    const renderedGroups = []
    const processedGroups = []
    _.forEach(groups, (group, groupIdx) => {
      if (!_.includes(processedGroups, groupIdx)) {
        const nextGroup = groups[groupIdx + 1] || {}
        const remaining = []
        const numItems = (group.items || []).length
        const numItemsNext = (nextGroup.items || []).length
        _.forEach(_.range(1, maxSpanCols + 1), (maxSpan) => {
          const rowsNeeded = Math.ceil(numItems / maxSpan)
          const rowsNeededNext = Math.ceil(numItemsNext / maxSpan)
          if (maxSpan === 1) {
            remaining.push(
              ((Math.ceil(numItems / rows) * rows) - numItems) +
              ((Math.ceil(numItemsNext / rows) * rows) - numItemsNext)
            )
          } else {
            remaining.push(
              ((rowsNeeded * maxSpan) - numItems) +
              ((rowsNeededNext * maxSpan) - numItemsNext)
            )
          }
        })
        const min = _.min(remaining)
        const posMin = _.indexOf(remaining, min)
        const colsNeeded = posMin + 1
        const currentGroups = [group, nextGroup]
        renderedGroups.push(
          <GroupsRenderer
            {...this.props}
            groups={currentGroups}
            key={groupIdx}
            index={groupIdx}
            styleOuter={{ flex: 'none', height: 'auto' }}
            styleInner={{ position: 'relative' }}
            styleButtonGrid={{ position: 'relative' }}
            getNecessaryRows={this.getNecessaryRows}
            styleTitle={{ fontSize: '2.5vmin', borderRadius: '5px', margin: '2%' }}
            styleTitleDescription={{ fontSize: '1.5vmin' }}
            applyTitleColor={true}
            showValue={true}
            showImage={true}
            addBgColor={false}
          />
        )
        processedGroups.push(groupIdx + 1)

        processedGroups.push(groupIdx)
        remainingCols -= colsNeeded
      }
    })
    this.appendRemainingCols(renderedGroups, remainingCols, cols, expandCol)
    return this.renderWithSeparators(renderedGroups)
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

  renderWithSeparators(renderedGroups) {
    const { cols, className } = this.props
    const grow = 0.5 / cols
    return (
      <div className={className}
        style={{ flexDirection: 'column', overflow: 'auto' }}>
        {_.flatMap(renderedGroups, (value, idx, array) =>
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
    return _.map(filteredGroups, (group) => {
      return Math.ceil((group.items || []).length / cols)
    })
  }
}

TotemNavigationGridRenderer.propTypes = {
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
  filterClass: PropTypes.string,
  buttonProps: PropTypes.object,
  groupHints: PropTypes.array,
  showTitle: PropTypes.bool
}

TotemNavigationGridRenderer.defaultProps = {
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

export default (TotemNavigationGridRenderer)
