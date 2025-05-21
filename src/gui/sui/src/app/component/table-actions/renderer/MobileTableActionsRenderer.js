import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'

import PopMenu from '../../../../component/pop-menu'
import ActionButton from '../../../../component/action-button/JssActionButton'
import TablePropTypes from '../../../../prop-types/TablePropTypes'
import { tableInState } from '../../../util/tableValidator'
import { TableStatus } from '../../../model/TableStatus'
import TableType from '../../../model/TableType'
import ButtonGrid from '../../button-grid/ButtonGrid'


export default class MobileTableActionsRenderer extends Component {
  constructor(props) {
    super(props)

    this.ref = null
    this.state = {
      menuVisible: false,

      refReceived: false
    }

    this.renderPopMenu = this.renderPopMenu.bind(this)
    this.setRef = this.setRef.bind(this)
  }

  renderPopMenu(otherActions) {
    const { classes } = this.props
    const optionsIcon = this.state.menuVisible ? 'fa-angle-down' : 'fa-angle-up'

    let popUpClass
    if (tableInState(this.props.table, TableStatus.Totalized)) {
      popUpClass = classes.outerPopUpContainerTotaled
    } else if (TableType.Tab === this.props.table.type) {
      popUpClass = classes.outerPopUpContainerProgressTab
    } else {
      popUpClass = classes.outerPopUpContainerProgress
    }

    return (
      <PopMenu
        controllerRef={this.ref}
        menuVisible={this.state.menuVisible}
        menuStyle={{ width: '100% !important' }}
        position={'above'}
        containerClassName={classes.popContainer}
        menuClassName={popUpClass}
      >
        <ActionButton
          className={'test_TableActions_OPTIONS'}
          buttonElement={this.setRef}
          selected={this.state.menuVisible}
          onClick={() => this.setState({ menuVisible: !this.state.menuVisible })}
        >
          <i className={`fas ${optionsIcon} fa-2x`}/>
          <br/>
          <I18N id={'$OPTIONS'}/>
        </ActionButton>
        <div className={classes.innerPopupContainer}>
          <ButtonGrid
            direction="row"
            cols={2}
            rows={Math.ceil(Object.keys(otherActions).length / 2)}
            buttons={otherActions}
            style={{ position: 'relative' }}
          />
        </div>
      </PopMenu>
    )
  }

  render() {
    const { table, tableActions } = this.props

    const doTotalAction = tableActions.find(action => action.key === 'doTotal')
    const addOrderAction = tableActions.find(action => action.key === 'addOrder')
    const deselectTableAction = tableActions.find(action => action.key === 'deselect')
    const abandonAction = tableActions.find(action => action.key === 'abandon')
    const changeTip = tableActions.find(action => action.key === 'changeTip')
    const reOpenTable = tableActions.find(action => action.key === 'reopen')
    const closeTable = tableActions.find(action => action.key === 'close')
    const totalReport = tableActions.find(action => action.key === 'totalReport')

    const otherActions = {}
    let index = 0
    tableActions.forEach((action) => {
      if (tableInState(table, TableStatus.Totalized)) {
        if (![changeTip, closeTable, reOpenTable, deselectTableAction, totalReport].includes(action)) {
          otherActions[index] = action
          index += 1
        }
      } else if (![doTotalAction, abandonAction, addOrderAction, deselectTableAction].includes(action)) {
        otherActions[index] = action
        index += 1
      }
    })

    let actionButton
    if (tableInState(table, TableStatus.Totalized)) {
      actionButton = closeTable != null && closeTable.props.disabled === false ? closeTable : reOpenTable
    } else {
      actionButton = doTotalAction.props.disabled === true ? abandonAction : doTotalAction
    }

    const buttons = {
      0: this.renderPopMenu(otherActions),
      1: actionButton,
      2: deselectTableAction,
      3: (tableInState(table, TableStatus.Totalized)) ? changeTip : addOrderAction
    }
    return (
      <ButtonGrid
        direction="row"
        cols={2}
        rows={2}
        buttons={buttons}
        style={{ position: 'relative' }}
      />
    )
  }

  setRef(ref) {
    this.ref = ref
  }
}

MobileTableActionsRenderer.propTypes = {
  classes: PropTypes.object,
  tableActions: PropTypes.array,
  table: TablePropTypes
}
