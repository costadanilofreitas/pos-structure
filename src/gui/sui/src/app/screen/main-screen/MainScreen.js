import React, { Component } from 'react'
import PropTypes from 'prop-types'

import ConfirmationScreen from '../confirmation-screen/ConfirmationScreen'
import MainScreenRenderer from './renderer'
import LoginScreen from '../login-screen'
import OperatorState from '../../model/OperatorState'
import { operatorIsNotInState } from '../../util/operatorValidator'
import { posIsInState } from '../../util/posValidator'
import OperatorPropTypes from '../../../prop-types/OperatorPropTypes'
import PosStatePropTypes from '../../../prop-types/PosStatePropTypes'
import Header from '../../component/header'
import Footer from '../../component/footer'
import Banner from '../../component/banner'
import Menu from '../../../app/model/Menu'
import OperatorScreen from '../operator-screen'
import ManagerScreen from '../manager-screen'
import WorkingModePropTypes from '../../../prop-types/WorkingModePropTypes'
import OrderState from '../../model/OrderState'
import TableScreen from '../table-screen'
import RecallScreen from '../recall-screen'
import OrderScreen from '../order-screen'
import { isCashierFunction, isTablePod } from '../../model/modelHelper'
import MessageBusPropTypes from '../../../prop-types/MessageBusPropTypes'
import TablePropTypes from '../../../prop-types/TablePropTypes'
import TenderScreen from '../tender-screen'
import SaleSummaryScreen from '../sale-summary-screen'
import StaticConfigPropTypes from '../../../prop-types/StaticConfigPropTypes'
import DeviceType from '../../../constants/Devices'
import OrderPropTypes from '../../../prop-types/OrderPropTypes'
import WelcomeScreen from '../welcome-screen'
import { getJoinedAvailableSaleTypes, getShortedSaleTypes } from '../../util/saleTypeConverter'


function getTotemContentScreen(operator, orderState, order, showConfirmation, cancelConfirmation, confirmationTimeout) {
  let content
  const contentId = Menu.ORDER

  function showConfirmationScreen() {
    let paidStateHistoryTimestamp
    if (order.StateHistory) {
      for (let i = 0; i < order.StateHistory.State.length; i++) {
        if (order.StateHistory.State[i]['@attributes'].state === 'PAID') {
          paidStateHistoryTimestamp = order.StateHistory.State[i]['@attributes'].timestamp
        }
      }
    }
    const dateTimestamp = new Date(paidStateHistoryTimestamp)
    dateTimestamp.setSeconds(dateTimestamp.getSeconds() + parseInt(confirmationTimeout, 10))
    const now = new Date()

    return now < dateTimestamp
  }

  if (orderState === OrderState.InProgress) {
    content = <OrderScreen key={'order'}/>
  } else if (orderState === OrderState.Totaled) {
    content = <SaleSummaryScreen/>
  } else if (orderState === OrderState.Paid && showConfirmationScreen()) {
    content = <ConfirmationScreen key={'confirmation'} cancelConfirmationScreen={cancelConfirmation}/>
  } else {
    content = <WelcomeScreen/>
  }

  return { content, contentId }
}


export default class MainScreen extends Component {
  constructor(props) {
    super(props)

    this.state = {
      showConfirmationScreen: true,
      displayedMessagesId: [],
      newMessagesCount: 0
    }
    this.cancelConfirmationScreen = this.cancelConfirmationScreen.bind(this)
    this.resetNewMessageCount = this.resetNewMessageCount.bind(this)
    this.handleOnPopState = this.handleOnPopState.bind(this)
    this.updateDisplayedMessages(false)
  }

  getContentScreen() {
    const { operator, selectedMenu, workingMode, orderState, posState, selectedTable } = this.props
    let content
    let contentId

    contentId = selectedMenu
    if (selectedMenu !== Menu.OPERATOR && selectedMenu !== Menu.MANAGER) {
      if (operatorIsNotInState(operator, OperatorState.LoggedIn) || (posIsInState(posState, 'BLOCKED'))) {
        contentId = Menu.LOGIN
      } else if (selectedMenu == null) {
        if (isCashierFunction(workingMode) && !isTablePod(workingMode)) {
          if (orderState === OrderState.Totaled || orderState === OrderState.InProgress) {
            contentId = Menu.ORDER
          } else {
            contentId = Menu.RECALL
          }
        } else if (isTablePod(workingMode) || selectedTable != null) {
          contentId = Menu.TABLE
        } else {
          contentId = Menu.ORDER
        }
      } else if (selectedMenu === Menu.ORDER && selectedTable != null) {
        contentId = Menu.TABLE
      }
    }

    switch (contentId) {
      case Menu.LOGIN: {
        content = <LoginScreen key={'login'}/>
        break
      }
      case Menu.OPERATOR: {
        content = <OperatorScreen key={'operator'}/>
        break
      }
      case Menu.MANAGER: {
        content = <ManagerScreen key={'manager'}/>
        break
      }
      case Menu.RECALL: {
        content = (
          <RecallScreen
            key={'recall'}
            newMessagesCount={this.state.newMessagesCount}
            resetMessageCount={this.resetNewMessageCount}
          />
        )
        break
      }
      case Menu.ORDER: {
        if (orderState === OrderState.Totaled) {
          content = <TenderScreen key={'tender'}/>
        } else {
          content = <OrderScreen key={'order'}/>
        }

        if (isCashierFunction(workingMode) && !isTablePod(workingMode)) {
          if (orderState === OrderState.InProgress || orderState === OrderState.Totaled) {
            content = <TenderScreen key={'tender'}/>
          } else {
            contentId = Menu.RECALL
          }
        }
        break
      }
      case Menu.TABLE: {
        if (orderState === OrderState.InProgress) {
          content = <OrderScreen key={'order'}/>
        } else {
          content = <TableScreen key={'table'}/>
        }
        break
      }
      default: {
        break
      }
    }

    return { content, contentId }
  }

  resetNewMessageCount() {
    this.setState({ newMessagesCount: 0 })
  }

  messageAlreadyDisplayed(messageId, displayedMessagesId) {
    return displayedMessagesId.some(displayedMessageId => displayedMessageId === messageId)
  }

  updateDisplayedMessages(updateNewMessages) {
    let currentMessagesCount = this.state.newMessagesCount
    const joinedSaleTypes = getJoinedAvailableSaleTypes(this.props.staticConfig.availableSaleTypes)
    const saleTypes = getShortedSaleTypes(joinedSaleTypes)
    if (!saleTypes.includes('DL')) {
      return
    }
    this.props.msgBus.parallelSyncAction('update_chat_messages').then(response => {
      if (response.ok && response.data) {
        for (let i = 0; i < response.data.length; i++) {
          const { displayedMessagesId } = this.state
          const messageData = response.data[i]
          const messageId = messageData.id
          const messageFromUser = messageData.from.toLowerCase() === 'store'

          if (!this.messageAlreadyDisplayed(messageId, displayedMessagesId) && !messageFromUser) {
            displayedMessagesId.push(messageId)
            this.setState({ displayedMessagesId: displayedMessagesId })
            currentMessagesCount += 1
          }
        }

        if (updateNewMessages) {
          this.setState({ newMessagesCount: currentMessagesCount })
        }
      } else {
        console.error('Error retrieving chat messages')
      }
    })
  }

  static getDerivedStateFromProps(props) {
    return props.deviceType === DeviceType.Totem ? { showConfirmationScreen: true } : {}
  }

  componentDidUpdate() {
    const { showConfirmationScreen } = this.state
    const {
      operator, orderState, selectedMenu, deviceType, order, staticConfig
    } = this.props

    let contentScreen
    if (deviceType === DeviceType.Totem) {
      const confirmationTimeout = staticConfig.totemConfigurations.confirmationScreen.timeout
      contentScreen = getTotemContentScreen(
        operator, orderState, order, showConfirmationScreen, this.cancelConfirmationScreen, confirmationTimeout)
    } else {
      contentScreen = this.getContentScreen()
    }
    const { contentId } = contentScreen

    if (selectedMenu !== contentId && contentId !== Menu.LOGIN) {
      this.props.changeMenu(contentId)
    }
  }

  render() {
    let headerType
    let contentScreen
    let hideInfoMessage = false

    const { showConfirmationScreen } = this.state
    const {
      operator, orderState, deviceType, order, staticConfig
    } = this.props
    if (deviceType === DeviceType.Totem) {
      const confirmationTimeout = staticConfig.totemConfigurations.confirmationScreen.timeout
      contentScreen = getTotemContentScreen(
        operator, orderState, order, showConfirmationScreen, this.cancelConfirmationScreen, confirmationTimeout)
    } else {
      contentScreen = this.getContentScreen()
    }

    const { content, contentId } = contentScreen

    const { infoMessage } = this.props

    if (infoMessage != null) {
      if (infoMessage.msg != null) {
        if (infoMessage.msg.includes('#SHOW|')) {
          hideInfoMessage = true
        }
      }
    }

    if (deviceType === DeviceType.Totem) {
      if ([OrderState.InProgress, OrderState.Totaled].includes(orderState)) {
        headerType = <Banner visible={true}/>
      } else {
        headerType = null
      }
    } else {
      headerType = <Header contentId={contentId} newMessagesCount={this.state.newMessagesCount}/>
    }

    return (
      <MainScreenRenderer deviceType={deviceType} staticConfig={this.props.staticConfig}>
        {headerType}
        {content}
        <Footer showVersion={true} showDrawer={true} hideInfoMessage={hideInfoMessage}/>
      </MainScreenRenderer>)
  }

  shouldComponentUpdate(nextProps) {
    if (nextProps.selectedTable !== this.props.selectedTable) {
      return true
    }

    return (nextProps.actionRunning.busy !== true)
  }

  componentDidMount() {
    window.history.pushState({ saleScreen: true }, '', '')
    window.addEventListener('popstate', this.handleOnPopState)
    this.interval = setInterval(() => this.updateDisplayedMessages(true), 5000)
  }

  // eslint-disable-next-line class-methods-use-this
  componentWillUnmount() {
    window.history.replaceState(null, '', '')
    window.onpopstate = null
  }

  handleOnPopState(event) {
    if (event && !event.handled) {
      window.history.pushState({ saleScreen: true }, '', '')
      if (this.props.orderState === OrderState.Totaled) {
        const { selectedTable } = this.props.selectedTable
        if (selectedTable != null) {
          this.props.msgBus.syncAction('reopen_table', this.props.selectedTable.id)
        } else {
          this.props.msgBus.syncAction('do_back_from_total')
        }
      }
    }
  }

  cancelConfirmationScreen() {
    this.setState({ showConfirmationScreen: false })
  }
}

MainScreen.propTypes = {
  operator: OperatorPropTypes,
  workingMode: WorkingModePropTypes,
  orderState: PropTypes.string,
  selectedMenu: PropTypes.string,
  deviceType: PropTypes.number,
  order: OrderPropTypes,
  actionRunning: PropTypes.object,
  posState: PosStatePropTypes,
  selectedTable: TablePropTypes,
  msgBus: MessageBusPropTypes,
  infoMessage: PropTypes.object,
  staticConfig: StaticConfigPropTypes,
  changeMenu: PropTypes.func
}
