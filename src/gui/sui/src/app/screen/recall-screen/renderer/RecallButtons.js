import { I18N } from '3s-posui/core'
import { FlexChild, FlexGrid } from '3s-widgets'
import React from 'react'
import PropTypes from 'prop-types'
import ActionButton from '../../../../component/action-button'
import {
  confirmedLogistic, isAwaitingCancellationLogistic,
  isAwaitingLogistic,
  isSearchingLogistic, isSentLogistic
} from '../../../../constants/LogisticStatus'

export default class RecallButtons extends React.Component {
  getOrderParsedProperties() {
    const { customProps, orderStatus, tab } = this.props

    const pickupType = customProps.PICKUP_TYPE != null ? customProps.PICKUP_TYPE : ''
    const needLogistic = customProps.NEED_LOGISTICS != null ? customProps.NEED_LOGISTICS : ''

    const orderVoidedByUser = customProps.VOID_REASON_ID != null
    const voidPartner = customProps.VOID_PARTNER != null
    const logisticStatus = customProps.LOGISTIC_INTEGRATION_STATUS
    const orderWithError = customProps.DELIVERY_ERROR_TYPE != null
    const isDeliveryOrder = pickupType.toUpperCase() === 'DELIVERY'
    const needLogistics = needLogistic.toLowerCase() !== 'false' && isDeliveryOrder

    let scheduleTime = null
    const scheduledOrder = customProps.ORDER_TYPE === 'A'
    if (scheduledOrder) {
      scheduleTime = customProps.SCHEDULE_TIME
    }

    const voidedOrder = (orderStatus === 4)
    const confirmedOrder = (tab === 'DLV_CONFIRMED')
    const producedOrder = (orderStatus === 5 && !orderVoidedByUser)
    let additionalClasses = ''
    if (voidPartner) {
      additionalClasses = classes.partnerVoided
    }

    return {
      orderVoidedByUser,
      voidPartner,
      isDeliveryOrder,
      logisticStatus,
      orderWithError,
      needLogistics,
      scheduleTime,
      voidedOrder,
      confirmedOrder,
      producedOrder,
      additionalClasses
    }
  }

  orderPreviewButton() {
    const { id } = this.props
    return (
      <FlexChild>
        <ActionButton executeAction={['do_preview_order', id]}>
          <I18N id="$ORDER_PREVIEW"/>
        </ActionButton>
      </FlexChild>
    )
  }

  orderVoidedByPartner() {
    const { orderVoidedByUser, voidPartner, orderWithError, confirmedOrder } = this.getOrderParsedProperties()
    const { classes } = this.props

    if (!orderWithError || !voidPartner || orderVoidedByUser || confirmedOrder) {
      return <></>
    }

    return (
      <FlexChild size={2} innerClassName={classes.scheduledTime}>
        <I18N id="$CANCELED_ORDER"/>
      </FlexChild>
    )
  }

  orderProduceButton() {
    const {
      orderVoidedByUser, voidPartner, producedOrder, confirmedOrder, orderWithError
    } = this.getOrderParsedProperties()
    const { id, orderStatus } = this.props

    if (confirmedOrder || orderWithError) {
      return <></>
    }

    return (
      <FlexChild>
        <ActionButton
          executeAction={['produce_delivery_order', id]}
          onActionFinish={this.props.retrieveOrders}
          disabled={(orderStatus !== 2) || orderVoidedByUser || voidPartner || producedOrder}
        >
          <I18N id="$PRODUCE_DELIVERY_ORDER"/>
        </ActionButton>
      </FlexChild>
    )
  }

  orderSendManualButton() {
    const { orderWithError, confirmedOrder } = this.getOrderParsedProperties()
    const { id } = this.props

    if (confirmedOrder || !orderWithError) {
      return <></>
    }

    const action = () => {
      this.props.msgBus.syncAction('doRecallNext', '', id, false)
        .then((response) => {
          if (response.data.toLowerCase() === 'true') {
            this.props.changeMenu(null)
          }
        })
    }

    return (
      <FlexChild>
        <ActionButton
          executeAction={action}
        >
          <I18N id="$SEND_MANUAL"/>
        </ActionButton>
      </FlexChild>
    )
  }

  orderLogisticButtons() {
    const {
      logisticStatus, needLogistics, confirmedOrder, orderWithError, producedOrder, voidedOrder
    } = this.getOrderParsedProperties()
    const { id, remoteId, customProps } = this.props

    const pickupType = customProps.PICKUP_TYPE.toUpperCase()

    if (confirmedOrder || orderWithError) {
      return <></>
    }

    const logisticButton = { isDisabled: false }
    const deliveryButton = { isDisabled: false }

    if (!needLogistics) {
      if (pickupType === 'DELIVERY') {
        logisticButton.isDisabled = true
        logisticButton.message = <I18N id="$LOGISTIC_BY_PARTNER"/>
      }
      if (isSentLogistic(logisticStatus) || pickupType !== 'DELIVERY') {
        deliveryButton.isDisabled = !producedOrder || voidedOrder
        deliveryButton.action = ['confirm_delivery_payment', id, remoteId]
        deliveryButton.message = <I18N id="$CONFIRM_DELIVERY"/>
      } else {
        deliveryButton.isDisabled = !producedOrder
        deliveryButton.action = ['send_logistic_remote_order', id]
        deliveryButton.message = <I18N id="$LOGISTIC_SEND"/>
      }
    } else if (isAwaitingLogistic(logisticStatus)) {
      logisticButton.action = ['select_logistic_partner', id]
      logisticButton.message = <I18N id="$LOGISTIC_REQUEST"/>

      deliveryButton.isDisabled = true
      deliveryButton.message = <I18N id="$LOGISTIC_WAITING"/>
    } else if (isSearchingLogistic(logisticStatus)) {
      logisticButton.isDisabled = true
      logisticButton.message = <I18N id="$LOGISTIC_SEARCHING"/>

      deliveryButton.isDisabled = true
      deliveryButton.message = <I18N id="$LOGISTIC_WAITING"/>
    } else if (confirmedLogistic(logisticStatus)) {
      logisticButton.action = ['cancel_logistic_remote_order', id]
      logisticButton.message = <I18N id="$LOGISTIC_CANCEL"/>

      deliveryButton.isDisabled = !producedOrder
      deliveryButton.action = ['send_logistic_remote_order', id]
      deliveryButton.message = <I18N id="$LOGISTIC_SEND"/>
    } else if (isSentLogistic(logisticStatus)) {
      logisticButton.isDisabled = true
      logisticButton.message = <I18N id="$LOGISTIC_SENT"/>

      deliveryButton.isDisabled = !producedOrder || voidedOrder
      deliveryButton.action = ['confirm_delivery_payment', id, remoteId]
      deliveryButton.message = <I18N id="$CONFIRM_DELIVERY"/>
    } else if (isAwaitingCancellationLogistic(logisticStatus)) {
      logisticButton.isDisabled = true
      logisticButton.message = <I18N id="$LOGISTIC_AWAITING_CANCELLATION"/>

      deliveryButton.isDisabled = true
      deliveryButton.message = <I18N id="$LOGISTIC_WAITING"/>
    }

    return (
      <>
        {logisticButton.message &&
        <FlexChild>
          <ActionButton
            executeAction={logisticButton.action}
            disabled={logisticButton.isDisabled}
            onActionFinish={this.props.retrieveOrders}
          >
            {logisticButton.message}
          </ActionButton>
        </FlexChild>
        }
        <FlexChild>
          <ActionButton
            executeAction={deliveryButton.action}
            disabled={deliveryButton.isDisabled}
            onActionFinish={this.props.retrieveOrders}
          >
            {deliveryButton.message}
          </ActionButton>
        </FlexChild>
      </>
    )
  }

  orderDeliveryTakeOutButton() {
    const { confirmedOrder, voidedOrder, isDeliveryOrder, orderWithError,
      scheduleTime } = this.getOrderParsedProperties()

    const { classes, customProps } = this.props

    if (confirmedOrder || voidedOrder || isDeliveryOrder || orderWithError || scheduleTime) {
      return <></>
    }

    const pickupType = customProps.PICKUP_TYPE.toUpperCase()

    return (
      <FlexChild size={1} innerClassName={classes.scheduledTime}>
        <I18N id={`$DELIVERY_${pickupType}`}/>
      </FlexChild>
    )
  }

  orderVoidButton() {
    const { remoteId, tab } = this.props

    const { confirmedOrder } = this.getOrderParsedProperties()

    if (confirmedOrder) {
      return <></>
    }

    return (
      <FlexChild>
        <ActionButton
          executeAction={['do_ask_void_remote_order', remoteId]}
          onActionFinish={this.props.retrieveOrders}
          disabled={tab === 'DLV_CONFIRMED'}
        >
          <I18N id="$CLEAR_ORDER" defaultMessage="Cancel"/>
        </ActionButton>
      </FlexChild>
    )
  }

  orderScheduledButton() {
    const { classes } = this.props
    const { scheduleTime, confirmedOrder, orderWithError } = this.getOrderParsedProperties()

    if (confirmedOrder || orderWithError || !scheduleTime) {
      return <></>
    }

    return (
      <FlexChild size={1} innerClassName={classes.scheduledTime}>
        <I18N id="$SCHEDULED_ORDER"/> {scheduleTime}
      </FlexChild>
    )
  }

  render() {
    const { classes } = this.props

    const { additionalClasses } = this.getOrderParsedProperties()

    return (
      <FlexGrid className={`${classes.buttonsContainer} ${additionalClasses}`}>
        {this.orderPreviewButton()}
        {this.orderVoidedByPartner()}
        {this.orderProduceButton()}
        {this.orderSendManualButton()}
        {this.orderDeliveryTakeOutButton()}
        {this.orderScheduledButton()}
        {this.orderLogisticButtons()}
        {this.orderVoidButton()}
      </FlexGrid>
    )
  }
}

RecallButtons.propTypes = {
  id: PropTypes.number,
  remoteId: PropTypes.string,
  orderStatus: PropTypes.number,
  customProps: PropTypes.object,
  tab: PropTypes.string,
  classes: PropTypes.object,
  changeMenu: PropTypes.func,
  retrieveOrders: PropTypes.func,
  msgBus: PropTypes.shape({
    syncAction: PropTypes.func.isRequired,
    parallelSyncAction: PropTypes.func.isRequired
  })
}
