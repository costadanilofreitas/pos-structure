import React, { Component } from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'

import { I18N } from '3s-posui/core'

import { IconStyle, CommonStyledButton } from '../../../constants/commonStyles'
import { TableStatus } from '../../model/TableStatus'
import TableActionsRenderer from './renderer'
import { getPriceList } from '../../util/specialCatalog'
import { isCashierFunction } from '../../model/modelHelper'
import WorkingModePropTypes from '../../../prop-types/WorkingModePropTypes'
import TablePropTypes from '../../../prop-types/TablePropTypes'
import { ensureArray } from '../../../util/renderUtil'
import StaticConfigPropTypes from '../../../prop-types/StaticConfigPropTypes'
import OrderPropTypes from '../../../prop-types/OrderPropTypes'


export default class TableActions extends Component {
  constructor(props) {
    super(props)

    this.deviceType = null
    this.buttons = null
    this.handleDeviceTypeResponse = this.handleDeviceTypeResponse.bind(this)
  }

  static createButton(key, action, labelId, icon, disabled, onClick) {
    return (
      <CommonStyledButton
        key={key}
        executeAction={[...action]}
        disabled={disabled}
        onClick={onClick}
        border={true}
        className={`test_TableActions_${key.toUpperCase()}`}
      >
        <IconStyle
          className={`fa-2x ${icon}`}
          aria-hidden="true"
          disabled={disabled
          }/>
        <br/>
        <I18N id={labelId}/>
      </CommonStyledButton>
    )
  }

  createButtons() {
    const { workingMode, selectedTable, staticConfig } = this.props
    const hasOrders = ensureArray(selectedTable.orders).length > 0

    return {
      'fiscalTable': (disabled) => TableActions.createButton(
        'fiscal_table',
        ['close_table', selectedTable.id, this.deviceType],
        '$FISCAL_TABLE',
        'fas fa-landmark',
        disabled == null ? selectedTable.dueAmount !== 0 : disabled),
      'close': (disabled) => TableActions.createButton(
        'close',
        ['close_table', selectedTable.id, this.deviceType],
        '$CLOSE_TABLE',
        'far fa-window-close',
        disabled == null ? selectedTable.dueAmount !== 0 : disabled),
      'reopen': (disabled) => TableActions.createButton(
        'reopen',
        ['reopen_table', selectedTable.id],
        '$REOPEN_TABLE',
        'fas fa-undo',
        disabled),
      'clearTenders': (disabled) => TableActions.createButton(
        'clearTenders',
        ['do_clear_service_tenders', selectedTable.id],
        '$CLEAR_TENDERS',
        'fas fa-eraser fa-2x',
        disabled == null ? ensureArray(selectedTable.serviceTenders).length <= 0 : disabled),
      'changeTip': (disabled) => TableActions.createButton(
        'changeTip',
        ['do_change_tip', selectedTable.id],
        '$CHANGE_TIP',
        'fas fa-book fa-2x',
        disabled == null ? ensureArray(selectedTable.serviceTenders).length > 0 : disabled),
      'totalReport': (disabled) => TableActions.createButton(
        'totalReport',
        ['total_report', selectedTable.id],
        '$TOTAL_REPORT',
        'fas fa-print',
        disabled == null ? !hasOrders || selectedTable.dueAmount === 0 : disabled),
      'addOrder': (disabled) => TableActions.createButton(
        'addOrder',
        ['create_table_order', selectedTable.id, getPriceList(this.props.specialCatalog, selectedTable)],
        '$ADD_ORDER',
        'fas fa-plus-square fa-2x',
        disabled == null ? isCashierFunction(workingMode) : disabled),
      'doTotal': (disabled) => TableActions.createButton(
        'doTotal',
        ['do_total_table', selectedTable.id],
        '$DO_TOTAL',
        'fas fa-dollar-sign fa-2x',
        disabled == null ? (selectedTable.orders.reduce((a, b) => a + (b.totalGross || 0), 0) <= 0) : disabled),
      'doTransfer': (disabled) => TableActions.createButton(
        'transfer',
        ['do_transfer_table', selectedTable.id],
        '$TRANSFER',
        'fas fa-exchange-alt fa-2x',
        disabled == null ? !hasOrders : disabled),
      'join': (disabled) => TableActions.createButton(
        'join',
        ['do_join_table', selectedTable.id],
        '$JOIN',
        'fas fa-link fa-2x',
        disabled),
      'abandon': (disabled) => TableActions.createButton(
        'abandon',
        ['do_abandon_table', selectedTable.id],
        '$ABANDON',
        'fas fa-trash fa-2x',
        disabled == null ? hasOrders : disabled),
      'deselect': () => TableActions.createButton(
        'deselect',
        ['deselect_table'],
        '$DESELECT_TABLE',
        'fas fa-arrow-circle-left fa-2x'),
      'changeOperator': (disabled) => TableActions.createButton(
        'changeOperator',
        ['change_table_operator', selectedTable.id],
        '$CHANGE_OPERATOR',
        'fas fa-user-tie fa-2x',
        disabled),
      'unlink': (disabled) => TableActions.createButton(
        'unlink',
        ['do_unlink_table', selectedTable.id],
        '$UNLINK',
        'fas fa-unlink fa-2x',
        disabled == null ? ensureArray(selectedTable.linkedTables).length <= 0 : disabled),
      'changeSeats': (disabled) => TableActions.createButton(
        'changeSeats',
        ['do_change_table_seats', selectedTable.id],
        '$CHANGE_SEATS',
        'fa fa-users fa-2x',
        disabled),
      'reorganize': (disabled) => TableActions.createButton(
        'reorganize',
        ['create_table_order', selectedTable.id],
        '$REORGANIZE',
        'fas fa-sort-numeric-down fa-2x',
        disabled == null ? !hasOrders : disabled,
        () => this.props.setSeatScreen(true)),
      'setPriceList': (disabled) => TableActions.createButton(
        'setPriceList',
        ['doSpecialTableCatalog'],
        '$SPECIAL_CATALOG_TABLE',
        'fa fa-birthday-cake fa-2x',
        disabled == null ? hasOrders || _.isEmpty(staticConfig.specialMenus) : disabled)
    }
  }

  render() {
    const { selectedTable, order } = this.props
    const tableActions = []

    this.buttons = this.createButtons()
    if (selectedTable.status === TableStatus.Totalized) {
      if ((order.CustomOrderProperties || {}).FISCALIZATION_DATE == null) {
        tableActions.push(this.buttons.fiscalTable())
        tableActions.push(this.buttons.reopen(false))
        tableActions.push(this.buttons.clearTenders(false))
      } else {
        tableActions.push(this.buttons.close())
        tableActions.push(this.buttons.reopen(true))
        tableActions.push(this.buttons.clearTenders(true))
      }
      tableActions.push(this.buttons.changeTip())
      tableActions.push(this.buttons.totalReport())
      if ((order.CustomOrderProperties || {}).FISCALIZATION_DATE == null) {
        tableActions.push(this.buttons.deselect(false))
      } else {
        tableActions.push(this.buttons.deselect(true))
      }

      return <TableActionsRenderer tableActions={tableActions} table={selectedTable}/>
    }

    const isTab = selectedTable.id.startsWith('TAB')
    if (isTab === true) {
      tableActions.push(this.buttons.addOrder())
      tableActions.push(this.buttons.doTotal())
      tableActions.push(this.buttons.doTransfer())
      tableActions.push(this.buttons.changeOperator(false))
      tableActions.push(this.buttons.join(false))
      tableActions.push(this.buttons.totalReport())
      tableActions.push(this.buttons.abandon())
      tableActions.push(this.buttons.deselect())
      return <TableActionsRenderer tableActions={tableActions} table={selectedTable}/>
    }

    if ([TableStatus.InProgress, TableStatus.Seated, TableStatus.Waiting2BSeated].includes(selectedTable.status)) {
      tableActions.push(this.buttons.addOrder())
      tableActions.push(this.buttons.doTotal())
      tableActions.push(this.buttons.doTransfer())
      tableActions.push(this.buttons.changeOperator(false))
      tableActions.push(this.buttons.unlink())
      tableActions.push(this.buttons.join(false))
      tableActions.push(this.buttons.changeSeats(false))
      tableActions.push(this.buttons.reorganize())
      tableActions.push(this.buttons.setPriceList())
      tableActions.push(this.buttons.totalReport())
      tableActions.push(this.buttons.abandon())
      tableActions.push(this.buttons.deselect(false))

      return <TableActionsRenderer tableActions={tableActions} table={selectedTable}/>
    }

    return null
  }

  componentDidMount() {
    if (window.mwapi != null) {
      window.getDeviceTypeCallBackTableActions = this.handleDeviceTypeResponse

      window.mwapi.getDeviceType('getDeviceTypeCallBackTableActions')
    }
  }

  handleDeviceTypeResponse(resultCode, message, payload) {
    if (resultCode === '0') {
      this.deviceType = payload
    }
  }
}

TableActions.propTypes = {
  posId: PropTypes.number,
  selectedTable: TablePropTypes,
  order: OrderPropTypes,
  setSeatScreen: PropTypes.func,
  specialCatalog: PropTypes.string,
  staticConfig: StaticConfigPropTypes,
  workingMode: WorkingModePropTypes
}

