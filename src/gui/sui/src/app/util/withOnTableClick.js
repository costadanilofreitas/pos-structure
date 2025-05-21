import React, { Component } from 'react'
import { connect } from 'react-redux'
import PropTypes from 'prop-types'

import { TableStatus } from '../model/TableStatus'
import DialogType from '../../constants/DialogType'
import WorkingModePropTypes from '../../prop-types/WorkingModePropTypes'

import withPosId from './withPosId'
import withShowDialog from '../../util/withShowDialog'
import withShowInfoMessage from '../../util/withShowInfoMessage'
import withShowTableInfo from './withShowTableInfo'
import withExecuteActionMessageBus from '../../util/withExecuteActionMessageBus'
import withShowTabs from './withShowTabs'
import withState from '../../util/withState'

import { isCashierFunction } from '../model/modelHelper'
import { FLOOR_PLAN_CHANGED, SHOW_TABS_CHANGED, TABLE_INFO_CHANGED } from '../../constants/actionTypes'
import TablePropTypes from '../../prop-types/TablePropTypes'


function withOnTableClick(ComponentClass) {
  class WithOnTableClick extends Component {
    constructor(props) {
      super(props)
      this.msgBus = props.msgBus

      this.handleOnTableClick = this.handleOnTableClick.bind(this)
      this.handleOnConfirmDialogClose = this.handleOnConfirmDialogClose.bind(this)
    }

    handleOnTableClick = (clickedTable) => {
      const { actionRunning, workingMode } = this.props

      if ((actionRunning != null) && (!!actionRunning.busy)) {
        return
      }

      const id = clickedTable.id != null ? clickedTable.id : clickedTable.tableId
      let showTableInfo = this.props.showTableInfo
      const floorPlanTabsAction = 'tabs'

      if (id === floorPlanTabsAction) {
        this.props.changeLayout(false)
        this.props.changeShowTabs(true)

        return
      }

      let canSelectTable = false
      if (this.props.selectedTable != null && this.props.selectedTable.id === id) {
        canSelectTable = true
      }

      if (!showTableInfo || canSelectTable) {
        let selectedTable
        this.props.tables[0].some(aTable => {
          if (aTable.id === id) {
            selectedTable = aTable
            return true
          }
          return false
        })

        if (selectedTable && (selectedTable.status === TableStatus.Available)) {
          if (isCashierFunction(workingMode)) {
            return
          }

          this.selectedTable = selectedTable
          this.props.msgBus.syncAction('start_service', this.selectedTable.id)
          return
        }

        if (selectedTable && (selectedTable.status === TableStatus.Closed)) {
          this.selectedTable = selectedTable
          this.props.showDialog({
            type: DialogType.Confirm,
            message: '$CONFIRM_SET_AVAILABLE',
            onClose: this.handleOnConfirmDialogClose
          })
          return
        }

        this.props.msgBus.syncAction('select_table', id).then(response => {
          if (response.ok && response.data !== 'False') {
            this.props.changeTableInfo(false)
            showTableInfo = false
          }
        })
      } else {
        this.props.msgBus.syncAction('get_table_picture', id)
      }
    }

    handleOnConfirmDialogClose(confirmed) {
      if (confirmed) {
        this.props.msgBus.syncAction('set_available', this.selectedTable.id)
      }
    }

    render() {
      return (<ComponentClass onTableClick={this.handleOnTableClick} {...this.props}/>)
    }
  }

  const table = PropTypes.shape({
    id: PropTypes.string,
    status: PropTypes.number
  })

  function mapDispatchToProps(dispatch) {
    return {
      changeLayout: (payload) => dispatch({ type: FLOOR_PLAN_CHANGED, payload: payload }),
      changeShowTabs: (payload) => dispatch({ type: SHOW_TABS_CHANGED, payload: payload }),
      changeTableInfo: (payload) => dispatch({ type: TABLE_INFO_CHANGED, payload: payload })
    }
  }

  function mapStateToProps(state) {
    return {
      actionRunning: state.actionRunning
    }
  }

  WithOnTableClick.propTypes = {
    actionRunning: PropTypes.object,
    tables: PropTypes.shape({
      all: PropTypes.arrayOf(table),
      available: PropTypes.arrayOf(table),
      inProgress: PropTypes.arrayOf(table),
      totaled: PropTypes.arrayOf(table),
      closed: PropTypes.arrayOf(table),
      tabs: PropTypes.arrayOf(table)
    }),
    msgBus: PropTypes.shape({
      syncAction: PropTypes.func.isRequired
    }).isRequired,
    posId: PropTypes.number.isRequired,
    showDialog: PropTypes.func,
    showInfoMessage: PropTypes.func,
    showTableInfo: PropTypes.bool,
    selectedTable: TablePropTypes,
    changeTableInfo: PropTypes.func,
    changeLayout: PropTypes.func.isRequired,
    showTabs: PropTypes.bool,
    changeShowTabs: PropTypes.func.isRequired,
    workingMode: WorkingModePropTypes
  }

  const withStateComponent = withState(WithOnTableClick, 'workingMode')
  const connectComponent = connect(mapStateToProps, mapDispatchToProps)(withStateComponent)
  const returnClass = withShowTabs(withShowInfoMessage(connectComponent))
  return withShowTableInfo(withPosId(withExecuteActionMessageBus(withShowDialog(returnClass))))
}


export default withOnTableClick
