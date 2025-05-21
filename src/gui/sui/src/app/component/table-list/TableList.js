import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import { FlexChild, FlexGrid } from '3s-widgets'

import TableStateFilter from './table-state-filter'
import TableStateList from './table-state-list'
import { TableStatus } from '../../model/TableStatus'
import WorkingModePropTypes from '../../../prop-types/WorkingModePropTypes'
import StaticConfigPropTypes from '../../../prop-types/StaticConfigPropTypes'

class TableList extends Component {
  containerStyle = {
    width: '100%',
    height: '100%',
    display: 'flex',
    flexFlow: 'column',
    position: 'absolute'
  }

  constructor(props) {
    super(props)
    let actualFilter = props.hasTables ? TableStatus.InProgress : TableStatus.tabs
    const filterTables = this.props.tables[actualFilter]
    if (actualFilter === 4 && filterTables.length === 0) {
      actualFilter = 1
    }
    this.state = {
      currentFilter: actualFilter
    }

    this.handleOnFilterChange = this.handleOnFilterChange.bind(this)
  }

  render() {
    const { currentFilter } = this.state
    const { workingMode, hasTables } = this.props

    const actualFilter = (this.props.showTabs || !hasTables) ? 'tabs' : currentFilter
    const filterTables = this.props.tables[actualFilter]

    return (
      <FlexGrid direction={'column'}>
        <FlexChild size={1}>
          <TableStateFilter
            onFilterChange={this.handleOnFilterChange}
            currentFilter={actualFilter}
            workingMode={workingMode}
            enableTabBtns={this.props.staticConfig.enableTabBtns || (hasTables !== null && !hasTables)}
            hasTables={hasTables}
          />
        </FlexChild>
        <FlexChild size={10}>
          <TableStateList tables={filterTables} onTableClick={this.props.onTableClick} workingMode={workingMode}/>
        </FlexChild>
      </FlexGrid>
    )
  }

  handleOnFilterChange(newFilter) {
    this.props.changeShowTabs(false)
    this.setState({ currentFilter: newFilter })
  }
}

const table = PropTypes.shape({
  id: PropTypes.string,
  status: PropTypes.number
})

TableList.propTypes = {
  tables: PropTypes.shape({
    all: PropTypes.arrayOf(table),
    available: PropTypes.arrayOf(table),
    inProgress: PropTypes.arrayOf(table),
    totaled: PropTypes.arrayOf(table),
    closed: PropTypes.arrayOf(table),
    tabs: PropTypes.arrayOf(table)
  }),
  hasTables: PropTypes.bool,
  workingMode: WorkingModePropTypes,
  staticConfig: StaticConfigPropTypes,
  onTableClick: PropTypes.func.isRequired,
  showTabs: PropTypes.bool,
  changeShowTabs: PropTypes.func.isRequired
}

function mapDispatchToProps(dispatch) {
  return {
    changeShowTabs: (payload) => dispatch({ type: 'SHOW_TABS_CHANGED', payload: payload })
  }
}

export default connect(null, mapDispatchToProps)(TableList)
