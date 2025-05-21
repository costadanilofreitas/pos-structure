import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'
import { ContextButton } from '3s-posui/widgets'
import { FlexChild, FlexGrid } from '3s-widgets'

import { IconStyle, CommonStyledButton } from '../../../../../constants/commonStyles'
import ActionButton from '../../../../../component/action-button'
import WorkingModePropTypes from '../../../../../prop-types/WorkingModePropTypes'
import { isDeliveryOrder } from '../../../../../util/orderUtil'
import { isOrderTakerFunction } from '../../../../model/modelHelper'
import TablePropTypes from '../../../../../prop-types/TablePropTypes'
import StaticConfigPropTypes from '../../../../../prop-types/StaticConfigPropTypes'
import { TotaledOrderRenderer, checkOrderItems } from '../common/TotaledOrderRenderer'
import { orderInState } from '../../../../util/orderValidator'
import OrderState from '../../../../model/OrderState'

export default class DesktopOrderFunctionsRenderer extends Component {
  optionsButton = <I18N id="$OPTIONS" defaultMessage="Options"/>

  render() {
    const { order, workingMode, staticConfig, selectedTable } = this.props

    const orderAttributes = order['@attributes']
    const orderIsInProgress = orderAttributes != null && orderAttributes.state === 'IN_PROGRESS'
    const orderIsTotaled = orderAttributes != null && orderAttributes.state === 'TOTALED'
    const orderHasTotalAmount = orderAttributes != null && parseFloat(orderAttributes.totalAmount) > 0
    const validOrder = orderHasTotalAmount && orderIsInProgress
    const preSaleStart = staticConfig.enablePreStartSale
    const isCashier = workingMode.posFunction === 'CS'

    if (orderIsTotaled) {
      return <TotaledOrderRenderer isCashier={isCashier}/>
    }

    if (orderIsInProgress || selectedTable != null || !preSaleStart) {
      return this.renderLineGridButtons(orderIsInProgress, validOrder)
    }

    return this.renderStartOrderBtn()
  }

  renderLineGridButtons(orderInProgress, validOrder) {
    const { onShowModifierScreen, modifierScreenOpen, selectedTable, workingMode, staticConfig } = this.props
    const { onFire, onHold, onDontMake, onCleanItemTags, onPriceOverwrite, onComment, onHighPriority } = this.props
    const { onChangeProductionCourse, voidOrClearOption, classes, selectedLine, selectedParent, order } = this.props
    const { isChangingOrder, themes, hasModifier } = this.props

    const changingOrder = isChangingOrder(order)
    const orderHasItems = checkOrderItems(order)
    const customProperties = order.CustomOrderProperties

    let showCourses = false
    if (staticConfig.productionCourses != null && staticConfig.enabledTags.indexOf('ProductionCourses') >= 0) {
      showCourses = true
    }

    const contextButtons = (
      <ContextButton
        className={'test_OrderFunctions_OPTIONS'}
        classNameButton={classes.functionButton}
        classNameButtonPressed={classes.pressedFunctionButton}
        style={{ height: '100%', width: '100%' }}
        styleContextMenu={{ border: '0', zIndex: '3', width: '100%' }}
        styleButton={{
          color: themes.commonStyledButtonColor,
          backgroundColor: themes.commonStyledButtonBackground,
          border: `1px solid ${themes.backgroundColor}`
        }}
        styleArrow={{ display: 'none' }}
        autoHeight={true}
        styleButtonArrow={{ color: themes.iconColor }}
        buttonText={this.optionsButton}
      >
        {(selectedTable != null && staticConfig.enabledTags.indexOf('HighPriority') >= 0) &&
        <CommonStyledButton
          className={'test_OrderFunctions_HIGH-PRIORITY'}
          onClick={() => onHighPriority()}
          disabled={selectedLine == null || changingOrder}
          border={true}
        >
          <IconStyle
            className="fas fa-star fa"
            aria-hidden="true"
            disabled={selectedLine == null || changingOrder}
          />
          <br/>
          <I18N id="$HIGH_PRIORITY"/>
        </CommonStyledButton>
        }
        {(selectedTable != null && staticConfig.enabledTags.indexOf('Hold') >= 0) &&
        <CommonStyledButton
          className={'test_OrderFunctions_HOLD-ITEM'}
          onClick={() => onHold()}
          disabled={selectedLine == null || changingOrder}
          border={true}
        >
          <IconStyle
            className="far fa-hand-paper fa"
            aria-hidden="true"
            disabled={selectedLine == null || changingOrder}
          />
          <br/>
          <I18N id="$HOLD_ITEM"/>
        </CommonStyledButton>
        }
        {(selectedTable != null && staticConfig.enabledTags.indexOf('Fire') >= 0) &&
        <CommonStyledButton
          className={'test_OrderFunctions_FIRE-ITEM'}
          onClick={() => onFire()}
          disabled={selectedLine == null || changingOrder}
          border={true}
        >
          <IconStyle
            className="fas fa-bolt fa"
            aria-hidden="true"
            disabled={selectedLine == null || changingOrder}
          />
          <br/>
          <I18N id="$FIRE_ITEM"/>
        </CommonStyledButton>
        }
        {selectedTable != null && staticConfig.enabledTags.indexOf('DontMake') >= 0 &&
        <CommonStyledButton
          className={'test_OrderFunctions_DONT-MAKE'}
          onClick={() => onDontMake()}
          disabled={selectedLine == null || changingOrder}
          border={true}
        >
          <IconStyle
            className="fas fa-ban fa"
            aria-hidden="true"
            disabled={selectedLine == null || changingOrder}
          />
          <br/>
          <I18N id="$DONT_MAKE"/>
        </CommonStyledButton>
        }
        {selectedTable != null && showCourses &&
        <CommonStyledButton
          className={'test_OrderFunctions_CHANGE-COURSE'}
          onClick={() => onChangeProductionCourse()}
          disabled={selectedLine == null || changingOrder}
          border={true}
        >
          <IconStyle
            className="fas fa-code-branch"
            aria-hidden="true"
            disabled={selectedLine == null || changingOrder}
          />
          <br/>
          {staticConfig.productionCourses.length > 1
            ? <I18N id="$CHANGE_COURSE"/>
            : <span>{staticConfig.productionCourses[Object.keys(staticConfig.productionCourses)[0]]}</span>
          }
        </CommonStyledButton>
        }
        {selectedTable != null && staticConfig.enabledTags.length > 0 &&
        <CommonStyledButton
          className={'test_OrderFunctions_CLEAR-HOLD-FIRE'}
          onClick={() => onCleanItemTags()}
          disabled={selectedLine == null}
          border={true}
        >
          <IconStyle
            className="fas fa-eraser fa"
            aria-hidden="true"
            disabled={selectedLine == null}
          />
          <br/>
          <I18N id="$CLEAR_HOLD_FIRE"/>
        </CommonStyledButton>
        }
        {(staticConfig.priceOverrideEnabled || this.props.deliveryEnabled()) &&
        <CommonStyledButton
          className={'test_OrderFunctions_OVERWRITE-PRICE'}
          onClick={() => onPriceOverwrite()}
          disabled={selectedLine == null || changingOrder}
          border={true}
        >
          <IconStyle
            className="fas fa-hand-holding-usd fa"
            aria-hidden="true"
            disabled={selectedLine == null || changingOrder}
          />
          <br/>
          <I18N id="$OVERWRITE_PRICE"/>
        </CommonStyledButton>
        }
        <CommonStyledButton
          className={'test_OrderFunctions_SPECIAL-INSTRUCTION'}
          onClick={() => onComment()}
          disabled={selectedLine == null || changingOrder}
          border={true}
        >
          <IconStyle
            className="far fa-comments fa"
            aria-hidden="true"
            disabled={selectedLine == null || changingOrder}
          />
          <br/>
          <I18N id="$SPECIAL_INSTRUCTION"/>
        </CommonStyledButton>
      </ContextButton>
    )

    let optionsButton
    if (staticConfig.enabledTags != null && (staticConfig.enabledTags.length || staticConfig.priceOverrideEnabled)) {
      if (selectedLine == null || !orderInProgress || (changingOrder && !this.selectedLineIsOnHold(selectedLine))) {
        optionsButton = this.renderDisabledOptionsButton()
      } else {
        optionsButton = contextButtons
      }
    } else {
      optionsButton = this.renderCommentButton(orderInProgress)
    }

    const isManualDelivery = isDeliveryOrder(order.CustomOrderProperties) && orderInState(order, OrderState.InProgress)

    return (
      <FlexGrid direction={'column'}>
        <FlexChild>
          <FlexGrid direction={'row'}>
            <FlexChild>
              <CommonStyledButton
                className={'test_OrderFunctions_DELETE-LINE'}
                disabled={selectedLine == null || !orderInProgress}
                onClick={this.props.onDeleteLine}
                border={true}
              >
                <IconStyle
                  className="far fa-minus-square fa"
                  aria-hidden="true"
                  disabled={selectedLine == null || !orderInProgress}
                />
                <br/>
                <I18N id="$DELETE_LINE"/>
              </CommonStyledButton>
            </FlexChild>
            <FlexChild>
              {optionsButton}
            </FlexChild>
            <FlexChild>
              <CommonStyledButton
                className={'test_OrderFunctions_MODIFY-ORDER'}
                onClick={onShowModifierScreen}
                disabled={!hasModifier(selectedParent) || !orderInProgress || changingOrder}
                border={true}
              >
                <IconStyle
                  className="fas fa-check fa"
                  aria-hidden="true"
                  disabled={!hasModifier(selectedParent) || !orderInProgress || changingOrder}
                />
                <br/>
                <I18N id={(modifierScreenOpen) ? '$DONE' : '$MODIFY'}/>
              </CommonStyledButton>
            </FlexChild>
          </FlexGrid>
        </FlexChild>
        <FlexChild>
          <FlexGrid direction={'row'}>
            <FlexChild>
              {selectedTable != null
                ?
                <CommonStyledButton
                  className={'test_OrderFunctions_SEAT-CHANGE'}
                  onClick={this.props.onSeatChange}
                  disabled={!!selectedTable.tabNumber || selectedLine == null || changingOrder}
                  border={true}
                >
                  <IconStyle
                    className="fas fa-users fa"
                    aria-hidden="true"
                    disabled={!!selectedTable.tabNumber || selectedLine == null || changingOrder}
                  />
                  <br/>
                  <I18N id="$SEAT_NUMBER"/>
                </CommonStyledButton>
                :
                <CommonStyledButton
                  className={'test_OrderFunctions_STORE-ORDER'}
                  executeAction={['doStoreOrder']}
                  onActionFinish={this.props.onStoredOrders}
                  disabled={!validOrder && !isManualDelivery}
                  border={true}
                >
                  <IconStyle
                    className="far fa-save fa"
                    aria-hidden="true"
                    disabled={!validOrder && !isManualDelivery}
                  />
                  <br/>
                  <I18N id="$SAVE"/>
                </CommonStyledButton>
              }
            </FlexChild>
            <FlexChild>
              <CommonStyledButton
                className={'test_OrderFunctions_VOID-ORDER'}
                onClick={this.props.onVoidOrder}
                disabled={!orderInProgress || (changingOrder && orderHasItems) || isManualDelivery}
                border={true}
              >
                <IconStyle
                  className="fa fa-times fa"
                  aria-hidden="true"
                  disabled={!orderInProgress || (changingOrder && orderHasItems) || isManualDelivery}
                />
                <br/>
                <I18N id="$CLEAR_ORDER"/>
              </CommonStyledButton>
            </FlexChild>
            <FlexChild>
              {selectedTable != null
                ?
                <CommonStyledButton
                  className={'test_OrderFunctions_SEND-ORDER'}
                  onClick={() => this.props.onSendOrder(true)}
                  disabled={!validOrder}
                  border={true}
                >
                  <IconStyle
                    className="fas fa-sign-out-alt"
                    aria-hidden="true"
                    disabled={!validOrder}
                  />
                  <br/>
                  {changingOrder ? <I18N id="$SAVE_AND_QUIT"/> : <I18N id="$SEND_AND_QUIT"/>}
                </CommonStyledButton>
                :
                <CommonStyledButton
                  className={'test_OrderFunctions_TOTAL-ORDER'}
                  disabled={!validOrder || isOrderTakerFunction(workingMode)}
                  onClick={isDeliveryOrder(customProperties) ? this.props.onProduce : this.props.onTotal}
                  border={true}
                >
                  <IconStyle
                    className="fas fa-dollar-sign"
                    aria-hidden="true"
                    disabled={!validOrder || isOrderTakerFunction(workingMode)}
                  />
                  <br/>
                  {isDeliveryOrder(customProperties) ? <I18N id="$PRODUCE_DELIVERY_ORDER"/> : <I18N id="$TOTAL"/>}
                </CommonStyledButton>
              }
            </FlexChild>
          </FlexGrid>
        </FlexChild>
        {selectedTable != null &&
        <FlexChild>
          <FlexGrid direction={'row'}>
            <FlexChild>
              {this.getSeatButton(changingOrder)}
            </FlexChild>
            <FlexChild>
              <CommonStyledButton
                className={'test_OrderFunctions_CLEAR-OPTION'}
                disabled={selectedLine == null || changingOrder}
                onClick={() => voidOrClearOption(selectedLine, true)}
                border={true}
              >
                <IconStyle
                  className="fas fa-trash fa"
                  aria-hidden="true"
                  disabled={selectedLine == null || changingOrder}
                />
                <br/>
                <I18N id="$CLEAR_OPTION"/>
              </CommonStyledButton>
            </FlexChild>
            <FlexChild>
              <CommonStyledButton
                className={'test_OrderFunctions_SAVE-ORDER'}
                onClick={this.props.onSendOrder}
                disabled={!validOrder}
                border={true}
              >
                <IconStyle
                  className="far fa-save fa"
                  aria-hidden="true"
                  disabled={!validOrder}
                />
                <br/>
                {changingOrder ? <I18N id="$SAVE"/> : <I18N id="$SEND"/>}
              </CommonStyledButton>
            </FlexChild>
          </FlexGrid>
        </FlexChild>
        }
      </FlexGrid>
    )
  }

  selectedLineIsOnHold(selectedLine) {
    if (selectedLine && selectedLine.customProperties) {
      if (selectedLine.customProperties.hold && selectedLine.customProperties.hold.toLowerCase() === 'true') {
        return true
      }
    }
    return false
  }

  renderStartOrderBtn() {
    return (
      <FlexGrid direction={'row'}>
        <FlexChild>
          <ActionButton
            className={'test_OrderFunctions_START-ORDER'}
            executeAction={this.props.onStartOrder}
          >
            <IconStyle className="far fa-play fa" aria-hidden="true"/><br/>
            <I18N id="$START_ORDER"/>
          </ActionButton>
        </FlexChild>
      </FlexGrid>
    )
  }

  renderDisabledOptionsButton = () => {
    return (
      <CommonStyledButton
        disabled={true}
        border={true}
      >
        {this.optionsButton}
      </CommonStyledButton>
    )
  }

  renderCommentButton = (orderInProgress) => {
    return (
      <ActionButton
        className={'test_OrderFunctions_SPECIAL-INSTRUCTION'}
        executeAction={this.props.onComment}
        disabled={this.props.selectedLine == null || !orderInProgress || !this.props.staticConfig.commentButton}
        onActionFinish={function () {
          this.closeContextMenu()
        }}
      >
        <IconStyle
          className="far fa-comments fa"
          aria-hidden="true"
          disabled={this.props.selectedLine == null || !orderInProgress || !this.props.staticConfig.commentButton}
        />
        <br/>
        <I18N id="$SPECIAL_INSTRUCTION"/>
      </ActionButton>
    )
  }

  getSeatButton = (isChangingOrder) => {
    let label = <I18N id="$NO_SEAT"/>
    if (this.props.selectedSeat) {
      label = <I18N id="$SEAT" values={{ 0: this.props.selectedSeat }}/>
    }

    let icon = <IconStyle className="fas fa-user-times fa" aria-hidden="true" />
    const cannotChangeSeat = !!this.props.selectedTable.tabNumber || isChangingOrder
    if (this.props.selectedSeat) {
      icon = <IconStyle className="fas fa-user fa" aria-hidden="true" disabled={cannotChangeSeat} />
    }

    return (
      <CommonStyledButton
        className={'test_OrderFunctions_SELECTED-SEAT'}
        onClick={this.props.onSeatIncrement}
        disabled={cannotChangeSeat}
        border={true}
      >
        {icon} <br/>
        {label}
      </CommonStyledButton>
    )
  }
}

DesktopOrderFunctionsRenderer.propTypes = {
  themes: PropTypes.object,
  classes: PropTypes.object,
  order: PropTypes.object,
  selectedTable: TablePropTypes,
  selectedLine: PropTypes.object,
  selectedParent: PropTypes.object,
  onShowModifierScreen: PropTypes.func,
  modifierScreenOpen: PropTypes.bool,
  selectedSeat: PropTypes.number,
  onSeatChange: PropTypes.func,
  onSeatIncrement: PropTypes.func,
  workingMode: WorkingModePropTypes,
  staticConfig: StaticConfigPropTypes,
  onStartOrder: PropTypes.func,
  onVoidOrder: PropTypes.func,
  onTotal: PropTypes.func,
  onProduce: PropTypes.func,
  onSendOrder: PropTypes.func,
  onDeleteLine: PropTypes.func,
  onPriceOverwrite: PropTypes.func,
  onComment: PropTypes.func,
  onHighPriority: PropTypes.func,
  onHold: PropTypes.func,
  onFire: PropTypes.func,
  onDontMake: PropTypes.func,
  onChangeProductionCourse: PropTypes.func,
  onCleanItemTags: PropTypes.func,
  voidOrClearOption: PropTypes.func,
  onStoredOrders: PropTypes.func,
  deliveryEnabled: PropTypes.func,
  isChangingOrder: PropTypes.func,
  hasModifier: PropTypes.func
}

DesktopOrderFunctionsRenderer.defaultProps = {
  selectedLine: {}
}
