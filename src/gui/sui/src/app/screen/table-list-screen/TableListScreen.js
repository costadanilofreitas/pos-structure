import React, { Component } from 'react'
import { connect } from 'react-redux'
import PropTypes from 'prop-types'


import TableListScreenRenderer from './renderer/'

class TableListScreen extends Component {
  constructor(props) {
    super(props)
    this.toggleLayout = this.toggleLayout.bind(this)
    this.toggleTableInfo = this.toggleTableInfo.bind(this)
    this.openTable = this.openTable.bind(this)
  }

  render() {
    const hasTables = this.hasTables()
    return (
      <TableListScreenRenderer
        toggleLayout={this.toggleLayout}
        toggleTableInfo={this.toggleTableInfo}
        openTable={this.openTable}
        hasTables={hasTables}
      />
    )
  }

  hasTables() {
    const { tables } = this.props
    return tables[0].length !== 0
  }

  componentDidMount() {
    const { showTableInfo } = this.props

    if (showTableInfo) {
      this.props.changeTableInfo(false)
    }
  }

  toggleLayout() {
    const newState = !this.props.floorPlan.active
    this.props.changeShowTabs(false)
    this.props.changeLayout(newState)
  }

  toggleTableInfo() {
    const showTableInfo = this.props.showTableInfo

    if (showTableInfo) {
      this.props.msgBus.syncAction('deselect_table').then(response => {
        if (response.ok && response.data === 'True') {
          setTimeout(() => this.props.changeTableInfo(false), 100)
        }
      })
    } else {
      this.props.changeTableInfo(true)
    }
  }

  openTable(tableId = '') {
    this.props.msgBus.syncAction('select_table', tableId)
  }
}

TableListScreen.propTypes = {
  changeLayout: PropTypes.func.isRequired,
  floorPlan: PropTypes.shape({
    active: PropTypes.bool,
    rotation: PropTypes.number,
    plan: PropTypes.object
  }),
  changeTableInfo: PropTypes.func.isRequired,
  showTableInfo: PropTypes.bool,
  changeShowTabs: PropTypes.func.isRequired,
  msgBus: PropTypes.shape({
    syncAction: PropTypes.func.isRequired
  }).isRequired,
  tables: PropTypes.object
}

function mapDispatchToProps(dispatch) {
  return {
    changeLayout: (payload) => dispatch({ type: 'FLOOR_PLAN_CHANGED', payload: payload }),
    changeTableInfo: (payload) => dispatch({ type: 'TABLE_INFO_CHANGED', payload: payload }),
    changeShowTabs: (payload) => dispatch({ type: 'SHOW_TABS_CHANGED', payload: payload })
  }
}

export default connect(null, mapDispatchToProps)(TableListScreen)
