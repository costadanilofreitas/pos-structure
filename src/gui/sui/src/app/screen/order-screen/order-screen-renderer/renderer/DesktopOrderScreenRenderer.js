import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { FlexChild, FlexGrid } from '3s-widgets'

import SaleType from '../../../../component/sale-type'
import OrderPropTypes from '../../../../../prop-types/OrderPropTypes'
import OrderFunctions from '../../../../component/order-functions'
import StaticConfigPropTypes from '../../../../../prop-types/StaticConfigPropTypes'
import OrderMenu from '../../../../component/order-menu'
import CustomSalePanel from '../../../../component/custom-sale-panel'
import TablePropTypes from '../../../../../prop-types/TablePropTypes'
import QtyButtons from '../../../../component/qty-buttons'
import { orderHasAttribute } from '../../../../util/orderValidator'
import OrderState from '../../../../model/OrderState'
import ProductsContainer from '../common/ProductsContainer'


export default class DesktopOrderScreenRenderer extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    const { order, selectedQty, onQtyChange, classes, selectedTable, staticConfig } = this.props

    let salePanelSize = 70
    let actionsSize = 30

    if (selectedTable == null) {
      salePanelSize = 80
      actionsSize = 20

      const hasAnOrder = order['@attributes'] != null && order['@attributes'].state === 'IN_PROGRESS'
      if (!hasAnOrder && staticConfig.enablePreStartSale) {
        salePanelSize = 90
        actionsSize = 10
      }
    }

    return (
      <FlexGrid direction={'row'}>
        <FlexChild size={1}>
          <FlexGrid direction={'row'}>
            <FlexChild size={5}>
              <FlexGrid direction={'column'}>
                <FlexChild size={10}>
                  <SaleType/>
                </FlexChild>
                <FlexChild size={salePanelSize}>
                  {this.getCustomSalePanel()}
                </FlexChild>
                <FlexChild size={actionsSize}>
                  {this.getOrderFunctions()}
                </FlexChild>
              </FlexGrid>
            </FlexChild>
            <FlexChild size={1} outerClassName={classes.quantityContainer}>
              <QtyButtons value={selectedQty} onChange={onQtyChange}/>
            </FlexChild>
          </FlexGrid>
        </FlexChild>
        <FlexChild size={2} outerClassName={classes.saleItemsContainer}>
          <FlexGrid direction={'column'}>
            <FlexChild size={1} innerClassName={classes.menuTabsContainer}>
              {this.getOrderMenu()}
            </FlexChild>
            <FlexChild size={9}>
              <ProductsContainer {...this.props}/>
            </FlexChild>
          </FlexGrid>
        </FlexChild>
      </FlexGrid>
    )
  }

  getOrderMenu() {
    const { rootGroups, selectedMenu, onMenuSelect, staticConfig, searchNavigation } = this.props

    return (
      <OrderMenu
        selectedMenu={selectedMenu}
        groups={rootGroups}
        onMenuSelect={onMenuSelect}
        navigationOptions={staticConfig.navigationOptions}
        searchNavigation={searchNavigation}
      />
    )
  }

  getOrderFunctions() {
    const { isModifiersDisplayed, isCombo } = this.props

    return (
      <OrderFunctions
        {...this.props}
        setSkipAutoSelect={(state) => this.setState({ skipAutoSelect: state })}
        modifierScreenOpen={isModifiersDisplayed && !isCombo}
      />
    )
  }

  getCustomSalePanel() {
    const { selectedLine, selectedParent, skipAutoSelect, onLineClick, order } = this.props
    const showSummary = orderHasAttribute(order, 'state') && order['@attributes'].state === OrderState.InProgress

    return (
      <CustomSalePanel
        order={order}
        selectedLine={selectedLine}
        selectedParent={selectedParent}
        showSummary={showSummary}
        showSummaryChange={false}
        showSummaryDelivery={false}
        showSummaryDiscount={false}
        showSummaryDue={false}
        showSummaryService={false}
        showSummaryTax={false}
        showSummaryTip={false}
        showSummarySubtotal={false}
        showSummaryTotal={true}
        centralizeSummaryTotal={true}
        showHoldAndFire={true}
        showNotRequiredOptions={true}
        autoSelectLine={true}
        showFinishedSale={false}
        showDiscountedPrice={true}
        skipAutoSelect={skipAutoSelect}
        onLineClicked={onLineClick}
      />
    )
  }
}

DesktopOrderScreenRenderer.propTypes = {
  order: OrderPropTypes,
  selectedLine: PropTypes.object,
  selectedParent: PropTypes.object,
  skipAutoSelect: PropTypes.bool,
  onLineClick: PropTypes.func,
  selectedTable: TablePropTypes,
  selectedQty: PropTypes.number,
  onQtyChange: PropTypes.func,
  isModifiersDisplayed: PropTypes.bool,
  isCombo: PropTypes.bool,
  rootGroups: PropTypes.oneOfType([PropTypes.array, PropTypes.object]),
  selectedMenu: PropTypes.number,
  onMenuSelect: PropTypes.func,
  staticConfig: StaticConfigPropTypes,
  classes: PropTypes.object,
  searchNavigation: PropTypes.bool
}
