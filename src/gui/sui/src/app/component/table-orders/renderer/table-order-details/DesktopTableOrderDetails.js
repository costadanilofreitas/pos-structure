import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'
import { FlexChild, FlexGrid } from '3s-widgets'

import { IconStyle } from '../../../../../constants/commonStyles'
import { TableStatus } from '../../../../model/TableStatus'
import OrderStatus from '../../../../model/OrderStatus'
import ActionButton from '../../../../../component/action-button'
import TableOrderHeader from '../table-order-header'
import { isCashierFunction } from '../../../../model/modelHelper'
import WorkingModePropTypes from '../../../../../prop-types/WorkingModePropTypes'
import CustomSalePanel from '../../../custom-sale-panel'
import StaticConfigPropTypes from '../../../../../prop-types/StaticConfigPropTypes'


export default class DesktopTableOrderDetails extends Component {
  constructor(props) {
    super(props)
  }

  renderOrderButtons() {
    const { tableStatus, order, workingMode, staticConfig } = this.props

    const orderState = parseInt(order['@attributes'].stateId, 10)
    if (![TableStatus.InProgress, TableStatus.Seated].includes(tableStatus) || orderState !== OrderStatus.Stored) {
      return null
    }

    const editOrderDisabled = isCashierFunction(workingMode) || !staticConfig.canEditOrder
    const cancelOrderDisabled = isCashierFunction(workingMode)

    return (
      <div style={{ height: '100%', display: 'flex' }}>
        <ActionButton
          className={'test_TableOrder_OPTIONS'}
          key="addOrder"
          disabled={editOrderDisabled}
          onClick={() => this.props.onOrderChange(order)}
          blockOnActionRunning={true}
        >
          <IconStyle
            className="fa fa-cog fa"
            aria-hidden="true"
            disabled={editOrderDisabled}
            secondaryColor
          />
          <br/>
          <I18N id={'$EDIT_ORDER'}/>
        </ActionButton>
        <ActionButton
          key="cancelOrder"
          disabled={cancelOrderDisabled}
          onClick={() => this.props.onOrderCancel(order)}
          blockOnActionRunning
          className={'test_TableOrder_CLEAR'}
        >
          <IconStyle
            className="fas fa-times fa"
            aria-hidden="true"
            disabled={cancelOrderDisabled}
            secondaryColor
          />
          <br/>
          <I18N id={'$CLEAR_ORDER'}/>
        </ActionButton>
        <ActionButton
          key="printOrder"
          onClick={() => this.props.onOrderPrint(order)}
          disabled={true}
          blockOnActionRunning
        >
          <IconStyle
            className="fas fa-print fa"
            aria-hidden="true"
            disabled={true}
          />
          <br/>
          <I18N id={'$PRINT'}/>
        </ActionButton>
      </div>
    )
  }

  render() {
    const { order, currentTime, tableStatus } = this.props
    const classes = this.props.classes || {}

    return (
      <div className={classes.orderContainer} key={`container_${order['@attributes'].orderId}`}>
        <FlexGrid direction={'column'}>
          <FlexChild size={85}>
            <FlexGrid direction={'column'}>
              <FlexChild outerClassName={classes.orderHeader} size={15}>
                <TableOrderHeader
                  order={order}
                  tableStatus={tableStatus}
                  currentTime={currentTime}
                  showExpand={false}
                />
              </FlexChild>
              <FlexChild size={85}>
                <div className={classes.salePanelOuterContainer}>
                  <CustomSalePanel
                    key={`sp_${order['@attributes'].orderId}`}
                    showSummary={false}
                    showSummaryDue={false}
                    showHeader={false}
                    showHoldAndFire={true}
                    customOrder={order}
                  />
                </div>
              </FlexChild>
            </FlexGrid>
          </FlexChild>
          <FlexChild size={15}>
            {this.renderOrderButtons()}
          </FlexChild>
        </FlexGrid>
      </div>
    )
  }
}

DesktopTableOrderDetails.propTypes = {
  order: PropTypes.object,
  tableStatus: PropTypes.number.isRequired,
  currentTime: PropTypes.object,
  workingMode: WorkingModePropTypes,
  staticConfig: StaticConfigPropTypes,

  onOrderChange: PropTypes.func,
  onOrderCancel: PropTypes.func,
  onOrderPrint: PropTypes.func,

  classes: PropTypes.object
}
