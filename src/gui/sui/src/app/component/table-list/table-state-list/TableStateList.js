import React, { Component } from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'

import TableItem from './table-item'
import UserLevel from '../../../model/UserLevel'
import { isCashierFunction } from '../../../model/modelHelper'
import WorkingModePropTypes from '../../../../prop-types/WorkingModePropTypes'
import StaticConfigPropTypes from '../../../../prop-types/StaticConfigPropTypes'

export default class TableStateList extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    const { classes, tables, operator, workingMode, staticConfig } = this.props
    const level = parseInt(operator.level, 10)
    let filteredList
    if (level >= UserLevel.Manager || isCashierFunction(workingMode) || staticConfig.canOpenTableFromAnotherOperator) {
      filteredList = tables
    } else {
      filteredList = _.filter(tables, table => (!table.userId
        || table.userId === operator.id)
        || ['Available'].indexOf(table.statusDescr) >= 0)
    }
    return (
      <div className={classes.containerStyle}>
        <div className={classes.containerListStyle}>
          {filteredList.map(table =>
            <TableItem
              key={table.id}
              {...table}
              onTableClick={this.props.onTableClick}
            />)}
        </div>
      </div>
    )
  }
}

TableStateList.propTypes = {
  classes: PropTypes.object,
  tables: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.string.isRequired,
    status: PropTypes.number.isRequired,
    tabId: PropTypes.string
  })).isRequired,
  operator: PropTypes.shape({
    id: PropTypes.string.isRequired,
    level: PropTypes.string
  }).isRequired,
  workingMode: WorkingModePropTypes,
  staticConfig: StaticConfigPropTypes,
  onTableClick: PropTypes.func.isRequired
}
