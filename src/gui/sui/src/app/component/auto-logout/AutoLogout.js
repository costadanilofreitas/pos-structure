import { Component } from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'

import { orderHasAttribute, orderInState } from '../../util/orderValidator'
import OrderState from '../../model/OrderState'
import OperatorPropTypes from '../../../prop-types/OperatorPropTypes'
import OrderPropTypes from '../../../prop-types/OrderPropTypes'
import { posIsNotInState } from '../../util/posValidator'
import StaticConfigPropTypes from '../../../prop-types/StaticConfigPropTypes'
import DeviceType from '../../../constants/Devices'
import { isDeliveryOrder } from '../../../util/orderUtil'

export default class AutoLogout extends Component {
  constructor(props) {
    super(props)

    this.timerId = null
    this.onTouch = this.onTouch.bind(this)
    this.timeoutCountdown = this.props.staticConfig.screenTimeout
    this.timeoutFunction = this.timeoutFunction.bind(this)
  }

  hasOpenedDialogOtherThanTimeoutDialog() {
    const { dialogs } = this.props
    const otherDialog = _.some(dialogs, ({ 'id': dlgid }) => (dlgid !== 'timeout_id'))
    return !!otherDialog
  }

  timeoutFunction = () => {
    const { operator, order, actionRunning, deviceType } = this.props
    const { cancelTimeoutWindow, screenTimeout } = this.props.staticConfig
    const emptyOrder = !orderHasAttribute(order, 'state')

    let orderSafeState
    let posSafeState

    if (deviceType === DeviceType.Totem) {
      orderSafeState = orderInState(order, OrderState.InProgress, OrderState.Totaled)
      posSafeState = true
    } else {
      orderSafeState = orderInState(order, OrderState.InProgress, OrderState.Stored, OrderState.Voided)
      posSafeState = posIsNotInState(this.props.posState, 'BLOCKED')
    }

    const operatorSafeState = operator && operator.state === 'LOGGEDIN'
    const hasOpenDialog = this.hasOpenedDialogOtherThanTimeoutDialog()
    const isActionRunning = actionRunning.busy === true
    const canLogout = (emptyOrder || orderSafeState) && !hasOpenDialog && !isActionRunning
    const hasTimeoutConfigured = (cancelTimeoutWindow !== -1 && screenTimeout !== -1)
    const isManualDelivery = isDeliveryOrder(order.CustomOrderProperties) && orderInState(order, OrderState.InProgress)

    if (posSafeState && operatorSafeState && canLogout && hasTimeoutConfigured && !isManualDelivery) {
      if (this.timeoutCountdown > 0 && this.timeoutCountdown <= cancelTimeoutWindow) {
        this.props.changeDialog({
          id: 'timeout_id',
          type: 'timeout',
          message: `${this.timeoutCountdown}`
        })
      }
      if (this.timeoutCountdown === 0) {
        this.props.abandonPos()
        setTimeout(() => this.props.closeDialog('timeout_id'), 500)
        this.onTouch()
      }
      if (this.timeoutCountdown > 0) {
        this.timeoutCountdown--
      }
    } else {
      this.timeoutCountdown = screenTimeout
    }
  }

  onTouch = () => {
    const { screenTimeout } = this.props.staticConfig
    this.timeoutCountdown = screenTimeout
  }

  componentWillUnmount() {
    window.onpopstate = null
    window.history.replaceState(null, '', '')
    window.removeEventListener('touchstart', this.onTouch, false)
    window.removeEventListener('click', this.onTouch, false)
    clearInterval(this.timerId)
  }

  // eslint-disable-next-line class-methods-use-this
  render() {
    return null
  }

  componentDidMount() {
    window.history.pushState({ saleScreen: true }, '', '')
    window.addEventListener('popstate', this.handleOnPopState)
    window.addEventListener('touchstart', this.onTouch)
    window.addEventListener('click', this.onTouch)
    this.timerId = setInterval(this.timeoutFunction, 1000)
  }
}

AutoLogout.propTypes = {
  operator: OperatorPropTypes,
  order: OrderPropTypes,
  changeDialog: PropTypes.func,
  closeDialog: PropTypes.func,
  abandonPos: PropTypes.func,
  dialogs: PropTypes.array,
  actionRunning: PropTypes.object,
  staticConfig: StaticConfigPropTypes,
  deviceType: PropTypes.number,
  posState: PropTypes.shape({
    id: PropTypes.string,
    period: PropTypes.string,
    state: PropTypes.string
  })
}
