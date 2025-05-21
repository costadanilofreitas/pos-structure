import React, { Component } from 'react'
import PropTypes from 'prop-types'

import HeaderRenderer from './renderer'
import { operatorIsInState, operatorIsNotInState } from '../../util/operatorValidator'
import OrderPropTypes from '../../../prop-types/OrderPropTypes'
import MessageBusPropTypes from '../../../prop-types/MessageBusPropTypes'
import { orderInState } from '../../util/orderValidator'
import OperatorPropTypes from '../../../prop-types/OperatorPropTypes'
import Menu from '../../../app/model/Menu'
import WorkingModePropTypes from '../../../prop-types/WorkingModePropTypes'
import PosStatePropTypes from '../../../prop-types/PosStatePropTypes'
import { posIsInState } from '../../util/posValidator'
import TablePropTypes from '../../../prop-types/TablePropTypes'
import {
  isFrontPod,
  isTablePod,
  isFullPod,
  isCashierFunction,
  isLoginTS,
  isLoginQS,
  isDrivePod,
  isOrderPod,
  isTotemPod
} from '../../model/modelHelper'
import { shallowIgnoreEquals } from '../../../util/renderUtil'
import StaticConfigPropTypes from '../../../prop-types/StaticConfigPropTypes'


export default class Header extends Component {
  constructor(props) {
    super(props)

    this.handleOnMenuClick = this.handleOnMenuClick.bind(this)
  }

  shouldComponentUpdate(nextProps) {
    if (!shallowIgnoreEquals(this.props, nextProps, 'order', 'msgBus', 'changeMenu', 'actionRunning')) {
      return true
    }

    const currOrder = this.props.order || {}
    const nextOrder = nextProps.order || {}
    return currOrder.state !== nextOrder.state
  }

  render() {
    return (
      <HeaderRenderer
        selectedMenu={this.props.contentId}
        onMenuClick={this.handleOnMenuClick}
        enabledMenus={this.buildEnabledMenus()}
        newMessagesCount={this.props.newMessagesCount}
      />
    )
  }

  handleOnMenuClick(selectedMenu) {
    const enabledMenus = this.buildEnabledMenus(this.props.operator, this.props.order)
    if (enabledMenus[selectedMenu] === false) {
      return
    }

    let promise
    let promiseMenu = selectedMenu

    if (selectedMenu === Menu.OPERATOR) {
      promise = this.props.msgBus.syncAction('navigate_to_operator_menu')
    } else if (selectedMenu === Menu.MANAGER) {
      promise = this.props.msgBus.syncAction('navigate_to_manager_menu')
    } else if (selectedMenu === Menu.ORDER || selectedMenu === Menu.TABLE) {
      if (operatorIsInState(this.props.operator, 'PAUSED')) {
        this.props.msgBus.syncAction('unpause_user', this.props.operator.id)
      }
      this.props.changeMenu(promiseMenu)
    } else if (selectedMenu === Menu.RECALL) {
      if (operatorIsInState(this.props.operator, 'PAUSED')) {
        promiseMenu = Menu.RECALL
        promise = this.props.msgBus.syncAction('unpause_user', this.props.operator.id)
      } else {
        this.props.changeMenu(Menu.RECALL)
      }
    } else if (selectedMenu === Menu.LOGIN) {
      promiseMenu = null
      if (operatorIsNotInState(this.props.operator, 'LOGGEDIN')) {
        this.props.changeMenu(null)
      } else if (isLoginQS(this.props.workingMode)) {
        this.props.changeMenu(Menu.LOGIN)
      } else {
        promise = this.props.msgBus.syncAction('pause_user')
      }
    }

    if (promise != null) {
      promise.then(result => {
        if (result.ok && result.data === 'True') {
          this.props.changeMenu(promiseMenu)
        }
      })
    }
  }

  checkOpenedTables() {
    const { tableLists } = this.props
    return (!('4' in tableLists) || tableLists['4'].length === 0)
  }

  buildEnabledMenus() {
    const { operator, order, workingMode, selectedTable, staticConfig, tableLists } = this.props

    const enabledMenus = {}
    enabledMenus[Menu.LOGIN] = true
    enabledMenus[Menu.ORDER] = true
    enabledMenus[Menu.TABLE] = true
    enabledMenus[Menu.RECALL] = true
    enabledMenus[Menu.OPERATOR] = true
    enabledMenus[Menu.MANAGER] = true

    if (posIsInState(this.props.posState, 'BLOCKED', 'CLOSED')) {
      enabledMenus[Menu.RECALL] = false
      enabledMenus[Menu.ORDER] = false
      if (tableLists) {
        if (this.checkOpenedTables()) {
          enabledMenus[Menu.TABLE] = false
        }
      }
    }

    if (operatorIsNotInState(operator, 'LOGGEDIN')) {
      if (operatorIsInState(operator, 'PAUSED')) {
        if (isLoginTS(workingMode)) {
          enabledMenus[Menu.ORDER] = false
          enabledMenus[Menu.TABLE] = false
          enabledMenus[Menu.RECALL] = false
        }
      } else {
        enabledMenus[Menu.ORDER] = false
        enabledMenus[Menu.TABLE] = false
        enabledMenus[Menu.RECALL] = false
      }
    } else if (orderInState(order, 'IN_PROGRESS', 'TOTALED')) {
      enabledMenus[Menu.LOGIN] = false
      enabledMenus[Menu.OPERATOR] = false
      enabledMenus[Menu.MANAGER] = false
      enabledMenus[Menu.RECALL] = false

      if (selectedTable == null) {
        enabledMenus[Menu.TABLE] = false
      } else {
        enabledMenus[Menu.ORDER] = false
      }
    }

    if (!isFullPod(workingMode)) {
      if (isFrontPod(workingMode) || isDrivePod(workingMode) || isTotemPod(workingMode)) {
        enabledMenus[Menu.TABLE] = false
      } else if (isTablePod(workingMode)) {
        enabledMenus[Menu.ORDER] = false
        enabledMenus[Menu.RECALL] = false
      } else {
        enabledMenus[Menu.TABLE] = false
        enabledMenus[Menu.ORDER] = false
      }
    }

    if (selectedTable != null && !isTotemPod(workingMode)) {
      enabledMenus[Menu.ORDER] = false
      enabledMenus[Menu.RECALL] = false

      if (this.props.showTableInfo != null && !this.props.showTableInfo) {
        enabledMenus[Menu.LOGIN] = false
        enabledMenus[Menu.OPERATOR] = false
        enabledMenus[Menu.MANAGER] = false
      }
    }

    if (isFrontPod(workingMode) || isFullPod(workingMode)) {
      if (orderInState(order, 'TOTALED') && order['@attributes'].podType !== 'TS') {
        enabledMenus[Menu.ORDER] = true
      }
    }

    if (isOrderPod(workingMode) && isCashierFunction(workingMode)) {
      enabledMenus[Menu.ORDER] = false
    }

    if (!staticConfig.recallButton) {
      enabledMenus[Menu.RECALL] = false
    }

    if (!staticConfig.operatorButton) {
      enabledMenus[Menu.OPERATOR] = false
    }

    return enabledMenus
  }
}

Header.propTypes = {
  contentId: PropTypes.string,
  operator: OperatorPropTypes,
  order: OrderPropTypes,
  msgBus: MessageBusPropTypes,
  workingMode: WorkingModePropTypes,
  posState: PosStatePropTypes,
  selectedTable: TablePropTypes,
  changeMenu: PropTypes.func,
  showTableInfo: PropTypes.bool,
  staticConfig: StaticConfigPropTypes,
  newMessagesCount: PropTypes.number,
  tableLists: PropTypes.object
}
