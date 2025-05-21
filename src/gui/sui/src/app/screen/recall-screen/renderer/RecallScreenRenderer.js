import { I18N } from '3s-posui/core'
import { DataTable } from '3s-posui/widgets'

import { FlexChild, FlexGrid, ScrollPanel } from '3s-widgets'
import _ from 'lodash'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import ActionButton from '../../../../component/action-button'
import DeviceType from '../../../../constants/Devices'
import StaticConfigPropTypes from '../../../../prop-types/StaticConfigPropTypes'
import WorkingModePropTypes from '../../../../prop-types/WorkingModePropTypes'
import { formatOrders } from '../../../../util/orderUtil'
import { normalizeToCompare } from '../../../../util/stringUtil'
import Chat from '../../../component/chat'
import OrderSearch from '../../../component/order-search'
import { isOrderTakerFunction } from '../../../model/modelHelper'
import RecallButtons from './RecallButtons'
import { SpinningIcon, StyledButton } from './StyledRecallScreenRenderer'
import { ArrowUp, ArrowUpContainer } from '../../../component/buttons/common/StyledCommonRenderer'


class RecallScreenRenderer extends PureComponent {
  constructor(props) {
    super(props)
    this.storeColumns = [
      {
        path: 'orderId',
        headerStyle: { width: 'calc(100% / 12 * 1.5)' },
        title: <I18N id="$ORDER" defaultMessage="Order Id"/>
      },
      {
        path: 'createdAtTime',
        headerStyle: { width: 'calc(100% / 12 * 2.5)' },
        title: <I18N id="$TIME" defaultMessage="Time"/>
      },
      {
        path: 'custom.CUSTOMER_NAME',
        headerStyle: { width: 'calc(100% / 12 * 3)' },
        title: <I18N id="$CUSTOMER" defaultMessage="Customer"/>,
        styleCell: { textTransform: 'uppercase' }
      },
      {
        path: null,
        title: <I18N id="$ACTIONS" defaultMessage="Actions"/>,
        headerStyle: { width: 'calc(100% / 12 * 5)' },
        onRenderCell: this.storeActionsRenderer
      }
    ]
    this.deliveryColumns = [
      {
        path: 'idDescription',
        headerStyle: { width: 'calc(100% / 12 * 1.5)' },
        title: <I18N id="$ORDER_STORE_REMOTE_ID" defaultMessage="Order (Store / REMOTE)"/>
      },
      {
        path: 'customerName',
        headerStyle: { width: 'calc(100% / 12 * 2)' },
        title: <I18N id="$CUSTOMER" defaultMessage="Customer"/>,
        styleCell: { textTransform: 'uppercase' }
      },
      {
        path: 'partner',
        headerStyle: { width: 'calc(100% / 12 * 1.5' },
        title: <I18N id="$PARTNER" defaultMessage="Partner"/>,
        styleCell: { textTransform: 'uppercase' }
      },
      {
        path: 'receiveTime',
        headerStyle: { width: 'calc(100% / 12 * 1)' },
        title: <I18N id="$HOUR" defaultMessage="Hour"/>
      },
      {
        path: null,
        headerStyle: { width: 'calc(100% / 12 * 1)' },
        title: ''
      },
      {
        path: null,
        title: <I18N id="$ACTIONS" defaultMessage="Actions"/>,
        headerStyle: { width: 'calc(100% / 12 * 5)' },
        onRenderCell: this.deliveryActionsRenderer
      }
    ]
    this.deliveryErrorColumns = [
      {
        path: 'idDescription',
        headerStyle: { width: 'calc(100% / 12 * 1.5)' },
        title: <I18N id="$ORDER_STORE_REMOTE_ID" defaultMessage="Order (Store / REMOTE)"/>
      },
      {
        path: 'customerName',
        headerStyle: { width: 'calc(100% / 12 * 2)' },
        title: <I18N id="$CUSTOMER" defaultMessage="Customer"/>,
        styleCell: { textTransform: 'uppercase' }
      },
      {
        path: 'partner',
        headerStyle: { width: 'calc(100% / 12 * 1.5)' },
        title: <I18N id="$PARTNER" defaultMessage="Partner"/>,
        styleCell: { textTransform: 'uppercase' }
      },
      {
        path: 'receiveTime',
        headerStyle: { width: 'calc(100% / 12 * 1)' },
        title: <I18N id="$HOUR" defaultMessage="Hour"/>
      },
      {
        path: 'deliveryErrorType',
        headerStyle: { width: 'calc(100% / 12 * 2)' },
        title: <I18N id="$ERROR" defaultMessage="Error"/>,
        onRenderCell: this.deliveryErrorTypeRenderer
      },
      {
        path: null,
        title: <I18N id="$ACTIONS" defaultMessage="Actions"/>,
        headerStyle: { width: 'calc(100% / 12 * 4)' },
        onRenderCell: this.deliveryActionsRenderer
      }
    ]
    this.deliveryConfirmedColumns = [
      {
        path: 'idDescription',
        headerStyle: { width: 'calc(100% / 12 * 1.5)' },
        title: <I18N id="$ORDER_STORE_REMOTE_ID" defaultMessage="Order (Store / REMOTE)"/>
      },
      {
        path: 'customerName',
        headerStyle: { width: 'calc(100% / 12 * 2)' },
        title: <I18N id="$CUSTOMER" defaultMessage="Customer"/>,
        styleCell: { textTransform: 'uppercase' }
      },
      {
        path: 'partner',
        headerStyle: { width: 'calc(100% / 12 * 1.5)' },
        title: <I18N id="$PARTNER" defaultMessage="Partner"/>,
        styleCell: { textTransform: 'uppercase' }
      },
      {
        path: 'receiveTime',
        headerStyle: { width: 'calc(100% / 12 * 1)' },
        title: <I18N id="$HOUR" defaultMessage="Hour"/>
      },
      {
        path: 'status',
        headerStyle: { width: 'calc(100% / 12 * 2)' },
        title: <I18N id="$STATUS" defaultMessage="Status"/>
      },
      {
        path: null,
        headerStyle: { width: 'calc(100% / 12 * 2)' },
        title: ''
      },
      {
        path: null,
        title: <I18N id="$ACTIONS" defaultMessage="Actions"/>,
        headerStyle: { width: 'calc(100% / 12 * 4)' },
        onRenderCell: this.deliveryActionsRenderer
      }
    ]

    this.state = {
      tab: '',
      orders: [],
      deliveryOrders: [],
      deliveryErrors: [],
      deliveryConfirmed: [],
      showSpinner: false,
      orderFilter: { size: 1, text: '' },
      backgroundLoading: false
    }
    this.timerId = null
    this.refreshCountdown = 30
    this.refreshFunction = this.refreshFunction.bind(this)
    this.retrieveOrders = this.retrieveOrders.bind(this)
    this.storeActionsRenderer = this.storeActionsRenderer.bind(this)
    this.deliveryActionsRenderer = this.deliveryActionsRenderer.bind(this)
    this.deliveryErrorTypeRenderer = this.deliveryErrorTypeRenderer.bind(this)
    this.cleanChangeMenu = this.cleanChangeMenu.bind(this)
  }

  flashSpinner() {
    this.setState({ showSpinner: true })
    setTimeout(() => this.setState({ showSpinner: false }), 500)
  }

  hasOpenedDialog() {
    const { dialogs, actionRunning } = this.props
    const { backgroundLoading } = this.state
    const isActionRunning = actionRunning.busy === true
    return ((dialogs.length > 0) || isActionRunning || backgroundLoading)
  }

  refreshFunction = () => {
    const hasOpenDialog = this.hasOpenedDialog()
    if (!hasOpenDialog) {
      if (this.refreshCountdown === 0) {
        this.retrieveOrders()
      } else if (this.refreshCountdown > 0) {
        this.refreshCountdown--
      }
    } else if (this.refreshCountdown < 3) {
      this.refreshCountdown = 3
    }
  }

  onRefresh = () => {
    this.refreshCountdown = 30
  }

  storeActionsRenderer = (line) => {
    const { classes, workingMode } = this.props
    const totalizeInRecall = !isOrderTakerFunction(workingMode)

    return (
      <FlexGrid className={classes.buttonsContainer}>
        <FlexChild>
          <ActionButton
            className={'test_RecallScreen_PREVIEW'}
            executeAction={['do_preview_order', line.orderId]}
            onActionFinish={(response) => this.cleanChangeMenu(response)}
          >
            <I18N id="$ORDER_PREVIEW" defaultMessage="Preview"/>
          </ActionButton>
        </FlexChild>
        <FlexChild>
          <ActionButton
            className={'test_RecallScreen_RECALL'}
            executeAction={() => this.handleDoRecallNext(line, totalizeInRecall)}
            onActionFinish={() => this.retrieveOrders(true)}
          >
            <I18N id="$RECALL" defaultMessage="Recall"/>
          </ActionButton>
        </FlexChild>
        <FlexChild>
          <ActionButton
            className={'test_RecallScreen_CANCEL'}
            executeAction={['do_void_stored_order', line.orderId, line.session.pos]}
            onActionFinish={() => this.retrieveOrders(true)}
          >
            <I18N id="$CLEAR_ORDER" defaultMessage="Cancel"/>
          </ActionButton>
        </FlexChild>
      </FlexGrid>
    )
  }

  handleDoRecallNext(line, totalizeInRecall) {
    this.props.msgBus.syncAction('doRecallNext', '', line.orderId, totalizeInRecall)
      .then(response => {
        this.cleanChangeMenu(response)
      })
  }

  deliveryActionsRenderer = (line) => {
    const { tab } = this.state
    const { customProps, remoteId, id, orderStatus } = line

    return (
      <RecallButtons
        {...{ ...this.props, tab, customProps, remoteId, id, orderStatus }}
        retrieveOrders={this.retrieveOrders}
      />
    )
  }

  deliveryErrorTypeRenderer = (line) => {
    if (line.deliveryErrorType == null) {
      line.deliveryErrorType = 'UNKNOWN'
    }

    return (
      <I18N id={`$DELIVERY_ERROR_${line.deliveryErrorType}`} defaultMessage={line.deliveryErrorType}/>
    )
  }


  handleRecallErrorOrder(orderId) {
    this.props.msgBus.syncAction('doRecallNext', '', orderId, false)
      .then(response => {
        this.cleanChangeMenu(response)
      })
  }

  cleanChangeMenu = (response) => {
    if (response.data.toLowerCase() === 'true') {
      this.props.changeMenu(null)
    }
  }

  retrieveOrders = (clean_cache = false) => {
    const deliveryEnabled = this.getAllSaleTypes(this.props.staticConfig.availableSaleTypes)
      .includes('DELIVERY')
    this.setState({
      backgroundLoading: true
    })

    let retrievals = [
      this.props.msgBus.parallelSyncAction('get_stored_orders', false, clean_cache)
        .then(response => ['storedOrders', response])
    ]
    if (deliveryEnabled) {
      retrievals = retrievals.concat([
        this.props.msgBus.parallelSyncAction('get_delivery_stored_orders')
          .then(response => ['deliveryStoredOrders', response]),
        this.props.msgBus.parallelSyncAction('get_delivery_errors_orders')
          .then(response => ['deliveryErrorsOrders', response]),
        this.props.msgBus.parallelSyncAction('get_delivery_confirmed_orders')
          .then(response => ['deliveryConfirmedOrders', response])
      ])
    }

    Promise.all(retrievals)
      .then((value) => {
        const previousOrderQuantity = [
          this.state.orders, this.state.deliveryOrders, this.state.deliveryErrors, this.state.deliveryConfirmed
        ].reduce((acc, cur) => cur.length + acc, 0)
        let nextOrderQuantity = 0
        const callbacks = {
          storedOrders: response => {
            if (response.ok && response.data !== '') {
              const orders = formatOrders(response.data)
              nextOrderQuantity += orders.length
              this.setState({ orders: orders })
              const storedOrdersCount = {}
              _.forEach(orders, (order) => {
                if (order.saleType != null && storedOrdersCount[order.saleType] == null) {
                  storedOrdersCount[order.saleType] = 1
                } else if (order.saleType != null) {
                  storedOrdersCount[order.saleType] += 1
                }
              })
              if (!_.isEmpty(storedOrdersCount)) {
                this.props.updateStoredOrdersCount(storedOrdersCount)
              }
            } else {
              console.error('Error retrieving stored orders')
            }
            this.setState({ loading: false })
          },
          deliveryStoredOrders: response => {
            if (response.ok && response.data !== '') {
              const orders = formatOrders(response.data)
              nextOrderQuantity += orders.length
              this.setState({ deliveryOrders: orders })
            } else {
              console.error('Error retrieving stored orders')
            }
          },
          deliveryErrorsOrders: response => {
            if (response.ok && response.data !== '') {
              const orders = formatOrders(response.data)
              nextOrderQuantity += orders.length
              this.setState({ deliveryErrors: orders })
            } else {
              console.error('Error retrieving delivery errors orders')
            }
          },
          deliveryConfirmedOrders: response => {
            if (response.ok && response.data !== '') {
              const orders = formatOrders(response.data)
              nextOrderQuantity += orders.length
              this.setState({ deliveryConfirmed: orders })
            } else {
              console.error('Error retrieving confirmed orders')
            }
          }
        }
        value.forEach(([k, v]) => callbacks[k](v))
        this.onRefresh()
        if (previousOrderQuantity !== nextOrderQuantity) {
          this.flashSpinner()
        }
        this.setState({ backgroundLoading: false })
      })
  }

  componentWillUnmount() {
    clearInterval(this.timerId)
  }

  componentDidMount() {
    const { staticConfig } = this.props
    const { tab } = this.state
    if (tab === '') {
      const availableSaleTypes = this.getAllSaleTypes(staticConfig.availableSaleTypes)
      if (availableSaleTypes.length > 0) {
        const firstAvailableSaleType = availableSaleTypes[0]
        if (['EAT_IN', 'TAKE_OUT'].includes(firstAvailableSaleType)) {
          this.setState({ tab: 'STORE' })
        } else {
          this.setState({ tab: firstAvailableSaleType })
        }
      }
    }
    this.timerId = setInterval(this.refreshFunction, 1000)
    this.retrieveOrders(true)
  }

  render() {
    const { classes, staticConfig, deviceType } = this.props
    const { orders, deliveryOrders, deliveryErrors, deliveryConfirmed } = this.state
    const availableSaleTypes = this.getAllSaleTypes(staticConfig.availableSaleTypes)

    const frontCounterOrdersCount = this.getOrdersBySaleType(orders, ['EAT_IN', 'TAKE_OUT'], availableSaleTypes).length
    const manualDeliverySalesCount = this.getManualDeliverySalesCount(orders, availableSaleTypes)
    const driveOrdersCount = this.getOrdersBySaleType(orders, ['DRIVE_THRU'], availableSaleTypes).length
    const deliveryOrdersCount = deliveryOrders.length
    const deliveryErrorsCount = deliveryErrors.length
    const storeOrdersCount = frontCounterOrdersCount + manualDeliverySalesCount
    const deliveryConfirmedCount = deliveryConfirmed.length
    const hasOrders = (orders || []).length > 0

    this.deliveryErrorColumns.find(x => x.path === 'deliveryErrorType').disabled = this.state.tab !== 'DLV_ERROR'
    const filterSize = this.state.orderFilter.size

    return (
      <FlexGrid direction={'column'}>
        <FlexChild size={filterSize} outerClassName={classes.titleContainer}>
          <OrderSearch value={this.state.orderFilter} onChange={orderFilter => this.setState({ orderFilter })}/>
        </FlexChild>
        <FlexChild size={1} outerClassName={classes.titleContainer}>
          <FlexGrid>
            {(['EAT_IN', 'TAKE_OUT'].some(x => availableSaleTypes.includes(x)) || storeOrdersCount > 0) &&
            <FlexChild size={3} innerClassName={classes.detailsTitle}>
              <StyledButton
                key={`order_${this.state.tab === 'STORE'}`}
                text={<I18N id="$STORE"/>}
                submenuActive={this.state.tab === 'STORE'}
                className={'test_RecallScreen_STORE'}
                onClick={() => this.setState({ tab: 'STORE' })}
                blockOnActionRunning
              >
                {storeOrdersCount > 0 && <p className={classes.numberCircle}><span>{storeOrdersCount}</span></p>}
                {this.state.tab === 'STORE' && <ArrowUpContainer><ArrowUp/></ArrowUpContainer>}
              </StyledButton>
            </FlexChild>}
            {availableSaleTypes.includes('DRIVE_THRU') &&
            <FlexChild size={3} innerClassName={classes.detailsTitle}>
              <StyledButton
                key={`order_${this.state.tab === 'DRIVE_THRU'}`}
                text={<I18N id="$DRIVE"/>}
                submenuActive={this.state.tab === 'DRIVE_THRU'}
                className={'test_RecallScreen_DRIVE-THRU'}
                onClick={() => this.setState({ tab: 'DRIVE_THRU' })}
                blockOnActionRunning
              >
                {driveOrdersCount > 0 && <p className={classes.numberCircle}><span>{driveOrdersCount}</span></p>}
                {this.state.tab === 'DRIVE_THRU' && <ArrowUpContainer><ArrowUp/></ArrowUpContainer>}
              </StyledButton>
            </FlexChild>}
            {availableSaleTypes.includes('DELIVERY') && deviceType !== DeviceType.Mobile &&
            <>
              <FlexChild size={3} innerClassName={classes.detailsTitle}>
                <StyledButton
                  key={`order_${this.state.tab === 'DELIVERY'}`}
                  text={<I18N id="$DELIVERY"/>}
                  submenuActive={this.state.tab === 'DELIVERY'}
                  className={'test_RecallScreen_DELIVERY'}
                  onClick={() => this.setState({ tab: 'DELIVERY' })}
                  blockOnActionRunning
                >
                  {deliveryOrdersCount > 0 &&
                    <p className={classes.numberCircle}><span>{deliveryOrdersCount}</span></p>
                  }
                  {this.state.tab === 'DELIVERY' && <ArrowUpContainer><ArrowUp/></ArrowUpContainer>}
                </StyledButton>
              </FlexChild>
              <FlexChild size={3} innerClassName={classes.detailsTitle}>
                <StyledButton
                  key={`order_${this.state.tab === 'DLV_ERROR'}`}
                  text={<I18N id="$DLV_ERROR"/>}
                  submenuActive={this.state.tab === 'DLV_ERROR'}
                  className={'test_RecallScreen_DVL-ERROR'}
                  onClick={() => this.setState({ tab: 'DLV_ERROR' })}
                  blockOnActionRunning
                >
                  {deliveryErrorsCount > 0
                  && <p className={classes.numberCircle}><span>{deliveryErrorsCount}</span></p>}
                  {this.state.tab === 'DLV_ERROR' && <ArrowUpContainer><ArrowUp/></ArrowUpContainer>}
                </StyledButton>
              </FlexChild>
              <FlexChild size={3} innerClassName={classes.detailsTitle}>
                <StyledButton
                  key={`order_${this.state.tab === 'DLV_CONFIRMED'}`}
                  text={<I18N id="$DLV_CONFIRMED"/>}
                  submenuActive={this.state.tab === 'DLV_CONFIRMED'}
                  className={'test_RecallScreen_DVL-CONFIRMED'}
                  onClick={() => this.setState({ tab: 'DLV_CONFIRMED' })}
                  blockOnActionRunning
                >
                  {deliveryConfirmedCount > 0
                  && <p className={classes.numberCircle}><span>{deliveryConfirmedCount}</span></p>}
                  {this.state.tab === 'DLV_CONFIRMED' && <ArrowUpContainer><ArrowUp/></ArrowUpContainer>}
                </StyledButton>
              </FlexChild>
            </>
            }
            {staticConfig.recallAppOrders &&
            <FlexChild size={3} innerClassName={classes.detailsTitle}>
              <StyledButton
                key={`order_${this.state.tab === 'ONLINE'}`}
                submenuActive={this.state.tab === 'ONLINE'}
                className={'test_RecallScreen_ONLINE'}
                onClick={() => this.setState({ tab: 'ONLINE' })}
                blockOnActionRunning
              >
                <I18N id="$APP"/>
              </StyledButton>
            </FlexChild>}
            <FlexChild size={1} innerClassName={classes.detailsTitle}>
              <StyledButton
                submenuActive={this.state.tab === 'SYNC'}
                className={'test_RecallScreen_SYNC'}
                onClick={() => this.retrieveOrders(true)}
              >
                <SpinningIcon className="fas fa-sync fa-2x" aria-hidden="true" spin={this.state.backgroundLoading}/>
              </StyledButton>
            </FlexChild>
          </FlexGrid>
        </FlexChild>
        <FlexChild size={11 - filterSize} outerClassName={classes.ordersCont} innerClassName={classes.ordersPanel}>
          {this.renderList(classes, hasOrders, orders)}
          {availableSaleTypes.includes('DELIVERY') &&
          <Chat resetMessageCount={this.props.resetMessageCount} newMessagesCount={this.props.newMessagesCount}/>
          }
        </FlexChild>
      </FlexGrid>
    )
  }

  getOrdersBySaleType(orders, saleType, availableSaleTypes, canShowManualDeliveryOrders = false) {
    const filteredOrders = []
    _.forEach(orders, (order) => {
      const canShowOrder = saleType.includes(order.saleType) && availableSaleTypes.includes(order.saleType)
      const manualDeliveryOrder = saleType.includes('EAT_IN') && this.isAManualDeliveryOrder(order)
      if (canShowOrder || (manualDeliveryOrder && canShowManualDeliveryOrders)) {
        filteredOrders.push(order)
      }
    })
    return filteredOrders
  }

  getManualDeliverySalesCount(orders, availableSaleTypes) {
    if (!availableSaleTypes.includes('DELIVERY')) {
      return 0
    }
    const manualDeliverySales = []
    _.forEach(orders, (order) => {
      if (this.isAManualDeliveryOrder(order)) {
        manualDeliverySales.push(order)
      }
    })
    return manualDeliverySales.length
  }

  isAManualDeliveryOrder(order) {
    return order.saleType === 'DELIVERY' && ('custom_properties' in order && !('PARTNER' in order.custom_properties))
  }

  isOrderProduced(order) {
    return order.orderStatus === 2 && order.customProps.VOID_REASON_ID == null
  }

  alertLines(orders) {
    const { tab } = this.state

    if (tab === 'DELIVERY') {
      const { staticConfig } = this.props
      const thresholdTime = staticConfig.timeToAlertRecallDeliveryIsIdle

      for (let i = 0; i < orders.length; i++) {
        if (this.isOrderProduced(orders[i])) {
          const splitOrderReceiveDate = orders[i].receiveTime.split(' ')[0].split('/')
          const formattedDate = `${splitOrderReceiveDate[2]}-${splitOrderReceiveDate[1]}-${splitOrderReceiveDate[0]}`
          const receiveDate = new Date(`${formattedDate}T${orders[i].receiveTime.split(' ')[1]}`)
          const thresholdDate = new Date(receiveDate.getTime() + (thresholdTime * 60000))
          const currentDate = new Date()
          orders[i].isAlert = currentDate.getTime() > thresholdDate.getTime()
        }
      }
    }

    return orders
  }

  setConfirmedStatus(orders) {
    for (let i = 0; i < orders.length; i++) {
      if (orders[i].customProps.VOID_REASON_ID) {
        orders[i].status = <I18N id="$CANCELED"/>
      } else {
        orders[i].status = <I18N id="$FINISHED_ORDER"/>
      }
    }
    return orders
  }

  renderOrderList(orders, saleType, columnType) {
    const { classes, staticConfig } = this.props
    const availableSaleTypes = this.getAllSaleTypes(staticConfig.availableSaleTypes)
    const canShowManualDeliveryOrders = availableSaleTypes.includes('DELIVERY')
    let filteredOrders = saleType.includes('DELIVERY')
      ? this.alertLines(orders)
      : this.getOrdersBySaleType(orders, saleType, availableSaleTypes, canShowManualDeliveryOrders)
    if (this.state.tab === 'DLV_CONFIRMED') {
      filteredOrders = this.setConfirmedStatus(filteredOrders)
    }
    filteredOrders = filteredOrders.filter(order => {
      return this.state.orderFilter.text === '' || Object.values({ ...order, ...(order.custom || {}) })
        .some(v => normalizeToCompare(v)
          .includes(normalizeToCompare(this.state.orderFilter.text)))
    })

    return (
      <div className={classes.orders}>
        <ScrollPanel styleCont={{ fontWeight: 'normal' }}>
          <DataTable
            style={{ borderCollapse: 'separate' }}
            styleHeaderRow={{ height: '7vmin' }}
            styleRow={{ height: '7vmin' }}
            columns={columnType}
            data={filteredOrders}
          />
        </ScrollPanel>
      </div>)
  }

  renderList(classes, hasOrders, orders) {
    if (this.state.showSpinner) {
      return <div className={classes.loadingSpinner}/>
    }

    const { deliveryOrders, deliveryErrors, deliveryConfirmed } = this.state

    const ordersLength = (orders || []).length
    const deliveryOrdersLength = (deliveryOrders || []).length
    const deliveryErrorsLength = (deliveryErrors || []).length
    const deliveryConfirmedLength = (deliveryConfirmed || []).length

    if (ordersLength === 0 && deliveryOrdersLength === 0 &&
      deliveryErrorsLength === 0 && deliveryConfirmedLength === 0) {
      return (
        <div className={classes.centeredDiv}>
          <I18N id="$NO_ORDERS_FOUND"/>
        </div>
      )
    }

    switch (this.state.tab) {
      case 'STORE': {
        return this.renderOrderList((orders || []), ['EAT_IN', 'TAKE_OUT'], this.storeColumns)
      }
      case 'DRIVE_THRU': {
        return this.renderOrderList((orders || []), ['DRIVE_THRU'], this.storeColumns)
      }
      case 'DELIVERY': {
        return this.renderOrderList((this.state.deliveryOrders || []), ['DELIVERY'], this.deliveryColumns)
      }
      case 'DLV_ERROR': {
        return this.renderOrderList((this.state.deliveryErrors || []), ['DELIVERY'], this.deliveryErrorColumns)
      }
      case 'DLV_CONFIRMED': {
        return this.renderOrderList((this.state.deliveryConfirmed || []), ['DELIVERY'], this.deliveryConfirmedColumns)
      }
      default: {
        return null
      }
    }
  }

  getAllSaleTypes(saleTypesConfig) {
    const allSaleTypes = []

    for (let i = 0; i < saleTypesConfig.length; i++) {
      for (let j = 0; j < Object.values(saleTypesConfig[i]).length; j++) {
        allSaleTypes.push(Object.values(saleTypesConfig[i])[j])
      }
    }

    return allSaleTypes
  }
}

RecallScreenRenderer.propTypes = {
  classes: PropTypes.object,
  dialogs: PropTypes.array,
  workingMode: WorkingModePropTypes,
  changeMenu: PropTypes.func,
  staticConfig: StaticConfigPropTypes,
  msgBus: PropTypes.shape({
    syncAction: PropTypes.func.isRequired,
    parallelSyncAction: PropTypes.func.isRequired
  }),
  actionRunning: PropTypes.object,
  updateStoredOrdersCount: PropTypes.func,
  newMessagesCount: PropTypes.number,
  resetMessageCount: PropTypes.func,
  deviceType: PropTypes.number
}

export default RecallScreenRenderer
