import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'
import { FlexChild, FlexGrid } from '3s-widgets'

import { orderHasAttribute } from '../../../util/orderValidator'
import Label from '../../../../component/label'
import PopMenu from '../../../../component/pop-menu'
import OrderState from '../../../model/OrderState'
import OrderPropTypes from '../../../../prop-types/OrderPropTypes'
import TablePropTypes from '../../../../prop-types/TablePropTypes'
import CustomSalePanel from '../../custom-sale-panel'
import TableType from '../../../model/TableType'

const ANIMATION_TIMEOUT = 300

function areSaleLinesDifferent(lastSaleLines, currentSaleLines) {
  if (lastSaleLines === currentSaleLines) {
    return false
  }
  if (lastSaleLines == null || currentSaleLines == null) {
    return true
  }
  if (lastSaleLines.length !== currentSaleLines.length) {
    return true
  }
  for (let i = 0; i < lastSaleLines.length; i++) {
    if (lastSaleLines[i].qty !== currentSaleLines[i].qty) {
      return true
    }
    if (lastSaleLines[i].partCode !== currentSaleLines[i].partCode) {
      return true
    }
    if (lastSaleLines[i].itemId !== currentSaleLines[i].itemId) {
      return true
    }
  }
  return false
}

export default class MobileOrderTotalRenderer extends Component {
  constructor(props) {
    super(props)

    this.ref = null
    this.setRef = this.setRef.bind(this)
    this.handleOnLineClicked = this.handleOnLineClicked.bind(this)
    this.startAnimation = this.startAnimation.bind(this)
    this.state = {
      animating: false
    }
    this.animationTimer = null
    this.alive = true
  }

  handleOrderTotal() {
    const { classes } = this.props

    if (this.props.saleLine !== -1) {
      return (
        <FlexGrid direction={'row'}>
          <FlexChild size={9} innerClassName={classes.underlineSaleLine}>
            <label>
              {this.props.saleLine.qty} {this.props.saleLine.productName}
            </label>
          </FlexChild>
          <FlexChild size={2} innerClassName={`${classes.underlineSaleLine} test_OrderTotalRenderer_SUBTOTAL`}>
            <Label style={'currency'} text={this.props.saleLine.total}/>
          </FlexChild>
        </FlexGrid>
      )
    }

    return null
  }

  componentDidUpdate(prevProps) {
    if (!prevProps.order) {
      return
    }
    if (areSaleLinesDifferent(prevProps.order.SaleLine, this.props.order.SaleLine)) {
      this.startAnimation()
    }
  }

  startAnimation() {
    const me = this
    function endAnimation() {
      if (!me.alive) {
        return
      }
      me.setState({ animating: false })
      me.animationTimer = null
    }
    function setAnimation() {
      me.setState({ animating: true })
      me.animationTimer = setTimeout(endAnimation, ANIMATION_TIMEOUT)
    }

    if (this.animationTimer) {
      clearTimeout(this.animationTimer)
      this.setState({ animating: false }, () => setTimeout(setAnimation, 0))
    } else {
      setAnimation()
    }
  }

  componentWillUnmount() {
    if (this.animationTimer) {
      clearTimeout(this.animationTimer)
    }
    this.alive = false
  }

  render() {
    const { classes, isSalePanelVisible, order, onToggleSalePanel, orderId, totalOrder } = this.props
    const { animating } = this.state
    const hasOrder = orderHasAttribute(order, 'state')
    const showSummary = hasOrder && order['@attributes'].state === OrderState.Totaled

    let titleId = ''
    if (this.props.selectedTable != null) {
      const table = this.props.selectedTable
      const tabText = table.tabNumber != null ? `$TAB_INFORMATION|${table.tabNumber}` : '$NEW_TAB'
      titleId = (table.type === TableType.Seat ? `$TABLE_INFORMATION|${table.id}` : tabText)
    }

    return (
      <PopMenu
        controllerRef={this.ref}
        menuVisible={isSalePanelVisible}
        position={'above'}
        containerClassName={classes.popContainer}
        menuClassName={classes.popupHeight}
      >
        <FlexGrid
          direction={'row'}
          onClick={onToggleSalePanel}
          gridRef={this.setRef}
          className={`${classes.container} ${animating ? classes.textBounce : ''}`}
        >
          <FlexChild size={10}>
            <FlexGrid direction={'column'}>
              {orderId === -1 && totalOrder === -1 &&
                <div className={classes.emptyCart}>
                  <I18N id={'$TOUCH_PRODUCT_TO_START_ORDER'}/>
                </div>
              }
              <FlexChild size={1} innerClassName={classes.saleLine}>
                <FlexGrid direction={'row'}>
                  <FlexChild size={11}>
                    {this.handleOrderTotal()}
                  </FlexChild>
                </FlexGrid>
              </FlexChild>
              <FlexChild size={1}>
                <FlexGrid direction={'row'}>
                  <FlexChild size={4} innerClassName={classes.orderId}>
                    <I18N id={titleId}/>
                  </FlexChild>
                  <FlexChild size={5} innerClassName={classes.orderId}>
                    {orderId !== -1 && <I18N id={`$ORDER_NUMBER|${orderId}`}/>}
                  </FlexChild>
                  <FlexChild size={2} innerClassName={`${this.props.classes.totalGross} test_OrderTotalRenderer_TOTAL`}>
                    <div>
                      <div>
                        {totalOrder !== -1 && <Label style={'currency'} text={totalOrder}/>}
                      </div>
                    </div>
                  </FlexChild>
                </FlexGrid>
              </FlexChild>
            </FlexGrid>
          </FlexChild>
          <FlexChild size={2}>
            <div className={classes.iconAngle}>
              {isSalePanelVisible ?
                <label>
                  <i className={'fas fa-angle-down fa-4x test_OrderTotalRenderer_DOWN'} />
                </label> :
                <label>
                  <i className={'fas fa-angle-up fa-4x test_OrderTotalRenderer_UP'} />
                </label>}
            </div>
          </FlexChild>
        </FlexGrid>
        <div className={classes.innerPopupContainer}>
          <CustomSalePanel
            order={order}
            selectedLine={this.props.selectedLine}
            selectedParent={this.props.selectedParent}
            showSummary={showSummary}
            showSummaryChange={showSummary}
            showSummaryDelivery={showSummary}
            showSummaryDiscount={showSummary}
            showSummaryDue={showSummary}
            showSummaryService={showSummary}
            showSummaryTax={showSummary}
            showSummaryTip={showSummary}
            showSummarySubtotal={showSummary}
            showSummaryTotal={showSummary}
            showHoldAndFire={true}
            showNotRequiredOptions={true}
            autoSelectLine={true}
            showFinishedSale={showSummary}
            showDiscountedPrice={true}
            skipAutoSelect={this.props.skipAutoSelect}
            onLineClicked={this.handleOnLineClicked}
            styleOverflow={true}
          />
        </div>
      </PopMenu>
    )
  }

  handleOnLineClicked(line, parentLine, userClicked) {
    this.props.onLineClick(line, parentLine, userClicked, false)
  }

  setRef(ref) {
    this.ref = ref
    this.forceUpdate()
  }
}

MobileOrderTotalRenderer.propTypes = {
  order: OrderPropTypes,
  totalOrder: PropTypes.number,
  classes: PropTypes.object,
  orderId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  saleLine: PropTypes.oneOfType([PropTypes.object, PropTypes.number]),
  onToggleSalePanel: PropTypes.func,
  isSalePanelVisible: PropTypes.bool,
  selectedTable: TablePropTypes,
  selectedLine: PropTypes.object,
  selectedParent: PropTypes.object,
  onLineClick: PropTypes.func,
  skipAutoSelect: PropTypes.bool
}

