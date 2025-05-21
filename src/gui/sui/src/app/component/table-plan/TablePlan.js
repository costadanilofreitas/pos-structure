import React, { Component } from 'react'
import { connect } from 'react-redux'
import PropTypes from 'prop-types'

import FloorPlan from './floor-plan/FloorPlan'
import { TableStatus } from '../../model/TableStatus'
import { showAlert, utcTimeNow } from '../../../util/timeFunctions'
import StaticConfigPropTypes from '../../../prop-types/StaticConfigPropTypes'
import TablePropTypes from '../../../prop-types/TablePropTypes'
import TableDetailsDialog from '../../../component/dialogs/table-details'

class TablePlan extends Component {
  constructor(props) {
    super(props)

    this.interval = null

    this.state = {
      time: utcTimeNow(),
      rotation: 0
    }
  }

  floorPlanOptions = (theme) => ({
    style: {
      stroke: 'black',
      fontSize: '1.5vmin'
    },
    styleCont: {
      border: '1px'
    },
    baseWidth: this.props.floorPlan.width,
    baseHeight: this.props.floorPlan.height,
    fillColors: {
      [TableStatus.Available]: theme.tableFillAvailable,
      [TableStatus.Totalized]: theme.tableFillTotaled,
      [TableStatus.Waiting2BSeated]: theme.tableFillWaiting2BSeated,
      [TableStatus.Seated]: theme.tableFillSeated,
      [TableStatus.InProgress]: theme.tableFillInProgress,
      [TableStatus.Linked]: theme.tableFillLinked,
      [100]: theme.tableFillIdleWarning,
      [101]: theme.tableFillIdle
    },
    strokeColors: {
      [TableStatus.Available]: theme.tableStrokeAvailable,
      [TableStatus.Totalized]: theme.tableStrokeTotaled,
      [TableStatus.Waiting2BSeated]: theme.tableStrokeWaiting2BSeated,
      [TableStatus.Seated]: theme.tableStrokeSeated,
      [TableStatus.InProgress]: theme.tableStrokeInProgress,
      [TableStatus.Linked]: theme.tableStrokeLinked,
      [100]: theme.tableStrokeIdleWarning,
      [101]: theme.tableStrokeIdle
    }
  })

  getTableStatus = () => {
    const { tables } = this.props
    const alertIsIdle = this.props.staticConfig.timeToAlertTableIsIdle
    const alertIsIdleWarning = this.props.staticConfig.timeToAlertTableIsIdleWarning

    return _.reduce(tables == null ? [] : tables[0], (acc, value) => {
      const accRef = acc
      accRef[value.id] = value.status

      if (value.statusDescr !== 'Available' && value.statusDescr !== 'Totaled') {
        if (showAlert(value.lastUpdateTS, this.state.time, alertIsIdle)) {
          accRef[value.id] = 101
        } else if (showAlert(value.lastUpdateTS, this.state.time, alertIsIdleWarning)) {
          accRef[value.id] = 100
        }
      }

      return accRef
    }, {})
  }

  render() {
    const { executeTableClick, floorPlan, selectedTable, theme } = this.props
    const posFunction = 'FC'
    const plan = floorPlan == null || floorPlan.plan == null ? null : floorPlan.plan[posFunction]

    return (
      <div style={{
        width: `calc(100% - 2 * ${theme.defaultPadding})`,
        height: `calc(100% - 2 * ${theme.defaultPadding})`,
        background: theme.backgroundColor,
        margin: theme.defaultPadding,
        marginLeft: 0,
        position: 'absolute'
      }}>
        <FloorPlan
          rotation={floorPlan.rotation}
          tableStatus={this.getTableStatus()}
          onTableClick={this.props.onTableClick}
          options={this.floorPlanOptions(theme)}
          plan={plan}
          lineFill={theme.lineFill}
          lineStroke={theme.lineStroke}
        />
        {!executeTableClick && selectedTable &&
          <TableDetailsDialog selectedTable={selectedTable} compact={true}/>
        }
      </div>
    )
  }

  componentDidMount() {
    const { executeTableClick, showTableInfo } = this.props

    if (!executeTableClick && !showTableInfo) {
      this.props.changeTableInfo(true)
    }

    this.interval = setInterval(() => this.setState({ time: utcTimeNow() }), 1000)
  }

  componentWillUnmount() {
    clearInterval(this.interval)
  }
}

function mapStateToProps(state) {
  return { floorPlan: state.floorPlan,
    workingMode: state.workingMode
  }
}

const table = PropTypes.shape({
  id: PropTypes.string,
  status: PropTypes.number
})

TablePlan.propTypes = {
  tables: PropTypes.shape({
    all: PropTypes.arrayOf(table),
    available: PropTypes.arrayOf(table),
    inProgress: PropTypes.arrayOf(table),
    totaled: PropTypes.arrayOf(table),
    closed: PropTypes.arrayOf(table),
    tabs: PropTypes.arrayOf(table)
  }),
  floorPlan: PropTypes.shape({
    active: PropTypes.bool,
    height: PropTypes.number,
    width: PropTypes.number,
    rotation: PropTypes.number,
    plan: PropTypes.object
  }),
  workingMode: PropTypes.shape({
    posFunction: PropTypes.string
  }),
  theme: PropTypes.object,
  onTableClick: PropTypes.func.isRequired,
  executeTableClick: PropTypes.bool.isRequired,
  staticConfig: StaticConfigPropTypes,
  changeTableInfo: PropTypes.func.isRequired,
  showTableInfo: PropTypes.bool,
  selectedTable: TablePropTypes
}

function mapDispatchToProps(dispatch) {
  return {
    changeTableInfo: (payload) => dispatch({ type: 'TABLE_INFO_CHANGED', payload: payload })
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(TablePlan)
