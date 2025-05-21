import React, { Component } from 'react'
import _ from 'lodash'
import PropTypes from 'prop-types'
import ButtonGrid from '../../button-grid/ButtonGrid'


class GroupsRenderer extends Component {
  render() {
    const {
      classes, styleTitle, filterClass, showTitle, cols, rows, groups, index, styleOuter, styleInner, styleCell,
      styleButtonGrid, getNecessaryRows, applyTitleColor, styleTitleDescription
    } = this.props
    const filteredGroups = this.getFilteredGroups(groups, filterClass)
    const necessaryRows = getNecessaryRows(filteredGroups, cols, rows)

    return (
      <div
        key={index}
        style={{
          position: 'relative',
          height: '100%',
          flexGrow: cols,
          flexBasis: 0,
          flexShrink: 0
        }}
      >
        <div
          style={{
            display: 'flex',
            position: 'relative',
            flexDirection: 'column',
            height: '100%'
          }}
        >
          {_.map(filteredGroups, (group, idxGroup) => {
            let groupStyleTitle = { ...styleTitle }
            if (applyTitleColor) {
              groupStyleTitle = { ...styleTitle, background: group.bgColor }
            }

            return (
              <div
                key={`${index}.${idxGroup}`}
                style={styleOuter}
              >
                <ButtonGrid
                  className={classes.navigationGridPadding}
                  direction="row"
                  cols={cols}
                  rows={necessaryRows[idxGroup]}
                  visibleRows={necessaryRows[idxGroup]}
                  buttons={this.getButtonsForGrid(group, `${index}.${idxGroup}`)}
                  title={(showTitle) ? this.getGroupName(group) : null}
                  styleTitle={groupStyleTitle}
                  styleTitleDescription={styleTitleDescription}
                  titleDescription={this.getGroupDescription(group)}
                  styleCell={styleCell}
                  style={styleInner}
                  styleButtonGrid={styleButtonGrid}
                />
              </div>
            )
          })}
        </div>
      </div>
    )
  }

  getGroupName(group) {
    return group.button_text != null ? group.button_text : group.name
  }

  getGroupDescription(group) {
    return group.navDescription != null ? group.navDescription : null
  }

  getFilteredGroups(groups, filterClass) {
    let filteredGroups = groups
    if (filterClass) {
      filteredGroups = _.filter(groups, (group) => _.includes(group.classes, filterClass))
      filteredGroups = _.map(filteredGroups, (group) => {
        return {
          ...group,
          items: _.filter(group.items, (item) => _.includes(item.classes, filterClass))
        }
      })
    }
    return filteredGroups
  }

  getButtonsForGrid = (group, idx) => {
    const { sellFunc, onRenderSaleButton, showImage, showValue, addBgColor } = this.props
    const items = group.items || []
    const groupName = group.name || group.text
    const buttons = _.zipObject(
      _.range(items.length),
      _.map(items, (item, buttonIdx) => {
        const key = `${idx}.${groupName}.${buttonIdx}`
        return onRenderSaleButton(item, key, showImage, showValue, addBgColor, sellFunc)
      })
    )
    return buttons
  }
}

GroupsRenderer.propTypes = {
  classes: PropTypes.object,
  styleOuter: PropTypes.object,
  styleInner: PropTypes.object,
  styleTitle: PropTypes.object,
  applyTitleColor: PropTypes.bool,
  styleTitleDescription: PropTypes.object,
  styleCell: PropTypes.object,
  styleButtonGrid: PropTypes.object,
  filterClass: PropTypes.string,
  showTitle: PropTypes.bool,
  cols: PropTypes.number,
  rows: PropTypes.number,
  groups: PropTypes.array,
  index: PropTypes.number,
  sellFunc: PropTypes.func,
  onRenderSaleButton: PropTypes.func,
  getNecessaryRows: PropTypes.func,
  showValue: PropTypes.bool,
  showImage: PropTypes.bool,
  addBgColor: PropTypes.bool
}

GroupsRenderer.defaultProps = {
  styleOuter: {},
  styleInner: {},
  styleTitle: {},
  applyTitleColor: false,
  styleTitleDescription: {},
  styleCell: {},
  styleButtonGrid: {},
  showTitle: true,
  cols: 9,
  rows: 9,
  showValue: false,
  showImage: false,
  addStyle: true
}

export default (GroupsRenderer)
