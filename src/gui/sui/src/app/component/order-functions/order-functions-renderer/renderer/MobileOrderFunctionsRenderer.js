import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'

import ActionButton from '../../../../../component/action-button'
import { isOrderTakerFunction } from '../../../../model/modelHelper'
import PopMenu from '../../../../../component/pop-menu'
import WorkingModePropTypes from '../../../../../prop-types/WorkingModePropTypes'
import TablePropTypes from '../../../../../prop-types/TablePropTypes'
import StaticConfigPropTypes from '../../../../../prop-types/StaticConfigPropTypes'
import { TotaledOrderRenderer } from '../common/TotaledOrderRenderer'
import ButtonGrid from '../../../button-grid/ButtonGrid'

export default class MobileOrderFunctionsRenderer extends Component {
  constructor(props) {
    super(props)
    this.ref = null

    this.state = {
      menuVisible: false
    }
    this.setRef = this.setRef.bind(this)
  }

  render() {
    const { selectedSeat, onVoidOrder, onVoidLast, onTotal, onSeatChange, onSendOrder, onDeleteLine, onPriceOverwrite,
      onComment, onSeatIncrement, onModify, workingMode, isSalePanelVisible, isModifiersDisplayed, saleType, order,
      selectedTable, isChangingOrder, staticConfig } = this.props
    const changingOrder = isChangingOrder(order)
    let buttons

    const orderIsTotaled = order != null && order.state === 'TOTALED'
    const isCashier = workingMode.posFunction === 'CS'

    if (orderIsTotaled) {
      return <TotaledOrderRenderer isCashier={isCashier}/>
    }

    const disabled = this.props.selectedLine == null || changingOrder
    const disabledDeleteLine = this.props.selectedLine == null
    const hasAnOrder = order != null && order['@attributes'] != null && order['@attributes'].state === 'IN_PROGRESS'
    const preSaleStart = staticConfig.enablePreStartSale

    let cols = 1
    if (!hasAnOrder && selectedTable == null && preSaleStart) {
      buttons = {
        0: this.createButton(
          'startOrder',
          '$START_ORDER',
          'far fa-play fa',
          false,
          this.props.onStartOrder,
          saleType)
      }
    } else if (!isSalePanelVisible && !isModifiersDisplayed) {
      const paymentButtonDisabled = isOrderTakerFunction(workingMode)
      cols = 4
      buttons = {
        0: this.createButton(
          'deleteLast',
          '$DELETE_LAST',
          'far fa-minus-square',
          !hasAnOrder,
          onVoidLast),
        1: selectedTable != null
          ? this.createButton(
            'incrementSeat',
            this.getSeatLabel(selectedSeat),
            this.getSeatIcon(selectedSeat),
            false,
            onSeatIncrement)
          : this.createButton(
            'saveOrder',
            '$SAVE',
            'far fa-save',
            !hasAnOrder,
            onSendOrder),
        2: this.createButton(
          'voidOrder',
          '$CLEAR_ORDER',
          'fa fa-times',
          !hasAnOrder,
          onVoidOrder),
        3: selectedTable != null
          ? this.createButton(
            'storeTableOrder',
            changingOrder ? '$SAVE' : '$SEND',
            'far fa-save',
            false,
            onSendOrder)
          : this.createButton(
            'totalOrder',
            '$TOTAL',
            'fas fa-dollar-sign',
            paymentButtonDisabled || !hasAnOrder,
            onTotal)
      }
    } else if (!isModifiersDisplayed) {
      cols = 4
      buttons = {
        0: this.createButton(
          'deleteLine',
          '$DELETE_LINE',
          'far fa-minus-square',
          !hasAnOrder || disabledDeleteLine,
          onDeleteLine),
        1: selectedTable != null
          ? this.createPopMenu(disabled)
          : this.createButton(
            'price',
            '$OVERWRITE_PRICE',
            'fas fa-hand-holding-usd',
            !staticConfig.priceOverrideEnabled,
            onPriceOverwrite),
        2: this.createButton(
          'modify',
          '$MODIFY',
          'fas fa-check',
          !hasAnOrder || !this.props.modifyEnabled || changingOrder,
          onModify),
        3: selectedTable != null
          ? this.createButton(
            'changeSeat',
            '$SEAT_NUMBER',
            'fas fa-users fa',
            disabled,
            onSeatChange)
          : this.createButton(
            'comment',
            '$SPECIAL_INSTRUCTION',
            'far fa-comments',
            disabled || !staticConfig.specialInstructionsEnabled,
            onComment)
      }
    } else {
      buttons = {
        0: this.createButton(
          'modify',
          '$DONE',
          'fas fa-check',
          changingOrder,
          onModify)
      }
    }

    return (
      <ButtonGrid
        direction="row"
        cols={cols}
        rows={1}
        buttons={buttons}
      />
    )
  }

  createPopMenu(disabled) {
    const { classes, onHighPriority, onHold, onFire, onDontMake, onChangeProductionCourse, onCleanItemTags,
      onComment, onPriceOverwrite, staticConfig } = this.props
    const contextButtons = {}
    let index = 0
    if (staticConfig.enabledTags.length > 0 || staticConfig.priceOverrideEnabled) {
      if (staticConfig.enabledTags.indexOf('HighPriority') >= 0) {
        contextButtons[index] = this.createButton(
          'highPriority',
          '$HIGH_PRIORITY',
          'fas fa-star',
          disabled,
          onHighPriority)
        index++
      }
      if (staticConfig.enabledTags.indexOf('DontMake') >= 0) {
        contextButtons[index] = this.createButton(
          'dontMake',
          '$DONT_MAKE',
          'fas fa-ban',
          disabled,
          onDontMake)
        index++
      }
      if (staticConfig.enabledTags.indexOf('Fire') >= 0) {
        contextButtons[index] = this.createButton(
          'fire',
          '$FIRE_ITEM',
          'fas fa-bolt',
          disabled,
          onFire)
        index++
      }
      if (staticConfig.enabledTags.indexOf('Hold') >= 0) {
        contextButtons[index] = this.createButton(
          'hold',
          '$HOLD_ITEM',
          'far fa-hand-paper',
          disabled,
          onHold)
        index++
      }
      if (staticConfig.enabledTags.indexOf('ProductionCourses') >= 0) {
        const courseLabel = staticConfig.productionCourses.length > 1
          ? '$CHANGE_COURSE'
          : staticConfig.productionCourses[Object.keys(staticConfig.productionCourses)[0]]
        contextButtons[index] = this.createButton(
          'courses',
          courseLabel,
          'fas fa-code-branch',
          disabled,
          onChangeProductionCourse)
        index++
      }
      if (staticConfig.enabledTags.length > 0) {
        contextButtons[index] = this.createButton(
          'clearHoldAndFire',
          '$CLEAR_HOLD_FIRE',
          'fas fa-eraser',
          disabled,
          onCleanItemTags)
        index++
      }
      if (staticConfig.priceOverrideEnabled || this.props.deliveryEnabled()) {
        contextButtons[index] = this.createButton(
          'price',
          '$OVERWRITE_PRICE',
          'fas fa-hand-holding-usd',
          disabled || !staticConfig.priceOverrideEnabled,
          onPriceOverwrite)
        index++
      }

      contextButtons[index] = this.createButton(
        'comment',
        '$SPECIAL_INSTRUCTION',
        'far fa-comments',
        disabled,
        onComment)
      index++

      if (index % 2 !== 0) {
        contextButtons[index] = (
          <ActionButton
            key={'place-holder'}
            disabled={true}
          >
          </ActionButton>
        )
      }

      const contextMenu = (
        <div className={classes.innerPopupContainer}>
          <ButtonGrid
            direction="row"
            cols={2}
            rows={Math.ceil(Object.keys(contextButtons).length / 2)}
            buttons={contextButtons}
            style={{ position: 'relative' }}
          />
        </div>
      )

      const heightPercentage = Math.floor(Object.keys(contextButtons).length / 2)
      const optionsIcon = this.state.menuVisible ? 'fa-angle-down' : 'fa-angle-up'
      return (
        <PopMenu
          controllerRef={this.ref}
          menuVisible={this.state.menuVisible}
          menuStyle={{ width: '100% !important', height: `calc(100% / 12 * ${heightPercentage})` }}
          position={'above'}
          containerClassName={classes.popContainer}
          menuClassName={classes.outerPopUpContainer}
        >
          <ActionButton
            buttonElement={this.setRef}
            selected={this.state.menuVisible}
            disabled={disabled}
            onClick={() => this.setState({ menuVisible: !this.state.menuVisible })}
          >
            <i className={`fas ${optionsIcon} fa-2x`}/>
            <br/>
            <I18N id={'$OPTIONS'}/>
          </ActionButton>
          {contextMenu}
        </PopMenu>
      )
    }
    const disableSpecialInstruction = disabled || !staticConfig.specialInstructionsEnabled
    return this.createButton('comment', '$SPECIAL_INSTRUCTION', 'far fa-comments', disableSpecialInstruction, onComment)
  }

  createButton(key, labelId, icon, disabled, onClick, ...onClickParameters) {
    let funcOnClick = onClick
    if (onClickParameters != null) {
      funcOnClick = () => onClick(onClickParameters)
    }

    let label = labelId
    if (typeof labelId === 'string') {
      label = <I18N id={labelId}/>
    }

    return (
      <ActionButton
        className={`test_OrderFunctions_${key.toUpperCase()}`}
        key={key}
        disabled={disabled}
        executeAction={funcOnClick}
      >
        <i className={`fa-2x ${icon}`} aria-hidden="true" style={{ margin: '0.5vh' }}/>
        <br/>
        {label}
      </ActionButton>
    )
  }

  getSeatLabel(selectedSeat) {
    if (selectedSeat) {
      return <I18N id="$SEAT" values={{ 0: selectedSeat }}/>
    }
    return <I18N id="$NO_SEAT"/>
  }

  getSeatIcon(selectedSeat) {
    if (selectedSeat) {
      return 'fa fa-user'
    }
    return 'fa fa-user-times'
  }

  setRef(ref) {
    this.ref = ref
  }
}

MobileOrderFunctionsRenderer.propTypes = {
  selectedSeat: PropTypes.number,
  selectedLine: PropTypes.object,
  workingMode: WorkingModePropTypes,
  order: PropTypes.object,
  onVoidOrder: PropTypes.func,
  onVoidLast: PropTypes.func,
  onTotal: PropTypes.func,
  onSeatChange: PropTypes.func,
  saleType: PropTypes.string,
  onSendOrder: PropTypes.func,
  onStartOrder: PropTypes.func,
  onDeleteLine: PropTypes.func,
  onPriceOverwrite: PropTypes.func,
  onComment: PropTypes.func,
  onSeatIncrement: PropTypes.func,
  onModify: PropTypes.func,
  onHold: PropTypes.func,
  onFire: PropTypes.func,
  onDontMake: PropTypes.func,
  onHighPriority: PropTypes.func,
  onChangeProductionCourse: PropTypes.func,
  onCleanItemTags: PropTypes.func,
  isSalePanelVisible: PropTypes.bool,
  isModifiersDisplayed: PropTypes.bool,
  modifyEnabled: PropTypes.bool,
  staticConfig: StaticConfigPropTypes,
  selectedTable: TablePropTypes,
  classes: PropTypes.object,
  deliveryEnabled: PropTypes.func,
  isChangingOrder: PropTypes.func
}
