import React, { Component } from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'

import { ensureArray } from '3s-posui/utils'
import { FlexChild, FlexGrid } from '3s-widgets'

import SaleType from '../../../../component/sale-type'
import OrderPropTypes from '../../../../../prop-types/OrderPropTypes'
import WorkingModePropTypes from '../../../../../prop-types/WorkingModePropTypes'
import MobileNavigation from '../../../../component/mobile-navigation'
import OrderTotal from '../../../../component/order-total'
import OrderFunctions from '../../../../component/order-functions'
import ItemModifier from '../../../../component/item-modifier'
import TablePropTypes from '../../../../../prop-types/TablePropTypes'
import QtyButtons from '../../../../component/qty-buttons'
import ActionButton from '../../../../../component/action-button/JssActionButton'
import StaticConfigPropTypes from '../../../../../prop-types/StaticConfigPropTypes'


export default class MobileOrderScreenRenderer extends Component {
  constructor(props) {
    super(props)

    this.renderOrderTotal = this.renderOrderTotal.bind(this)
    this.renderModifierScreen = this.renderModifierScreen.bind(this)
    this.renderBarcodeButton = this.renderBarcodeButton.bind(this)
    this.renderProductScreen = this.renderProductScreen.bind(this)
  }

  render() {
    const { isModifiersDisplayed } = this.props
    return isModifiersDisplayed ? this.renderModifierScreen() : this.renderProductScreen()
  }

  renderOrderTotal() {
    return (
      <OrderTotal
        onToggleSalePanel={this.props.onToggleSalePanel}
        isSalePanelVisible={this.props.isSalePanelVisible}
        selectedTable={this.props.selectedTable}
        selectedLine={this.props.selectedLine}
        selectedParent={this.props.selectedParent}
        onLineClick={this.props.onLineClick}
        skipAutoSelect={this.props.skipAutoSelect}
        customerName={this.props.customerName}
        workingMode={this.props.workingMode}
      />
    )
  }

  renderModifierScreen() {
    const { selectedQty, onQtyChange, selectedLine, onSellOption, voidOrClearOption, onSellModifier } = this.props
    const filteredSaleLines = _.filter(ensureArray(this.props.order.SaleLine), saleLine => {
      return selectedLine.lineNumber === saleLine['@attributes'].lineNumber
    })

    return (
      <FlexGrid direction={'column'}>
        <FlexChild size={9}>
          <ItemModifier
            saleLines={filteredSaleLines}
            selectedLine={selectedLine}
            onSellOption={onSellOption}
            voidOrClearOption={voidOrClearOption}
            onSellModifier={onSellModifier}
            selectedQty={selectedQty}
            onQtyChange={onQtyChange}
            onLineClick={this.props.onLineClick}
          />
        </FlexChild>
        <FlexChild size={1}>
          {this.renderOrderTotal()}
        </FlexChild>
        <FlexChild size={1}>
          <OrderFunctions {...this.props} />
        </FlexChild>
      </FlexGrid>
    )
  }

  renderBarcodeButton() {
    const { classes, onAskBarcode } = this.props

    return (
      <div className={classes.container}>
        <ActionButton
          key={'askBarcode'}
          className={`${classes.tabButtonStyle} ${classes.submenu}`}
          onClick={onAskBarcode}
          blockOnActionRunning={true}
        >
          <i className="fas fa-barcode fa-4x"/>
        </ActionButton>
      </div>
    )
  }

  renderProductScreen() {
    const { classes, onUnselectLine, onSellItem, selectedQty, onQtyChange, staticConfig, products,
      defaultNavigationIdx } = this.props
    return (
      <FlexGrid direction={'column'}>
        <FlexChild size={1}>
          <FlexGrid direction={'row'}>
            <FlexChild size={2}>
              <SaleType order={this.props.order}/>
            </FlexChild>
            <FlexChild size={1}>
              <QtyButtons value={selectedQty} onChange={onQtyChange}/>
            </FlexChild>
            {staticConfig.navigationOptions.showBarcodeScreen &&
            <FlexChild size={1}>
              {this.renderBarcodeButton()}
            </FlexChild>}
          </FlexGrid>
        </FlexChild>
        <FlexChild size={8} outerClassName={classes.saleItemsContainerMobile}>
          <MobileNavigation
            onSellItem={onSellItem}
            onUnselectLine={onUnselectLine}
            products={products}
            defaultNavigationIdx={defaultNavigationIdx}
          />
        </FlexChild>
        <FlexChild size={1}>
          {this.renderOrderTotal()}
        </FlexChild>
        <FlexChild size={1}>
          <OrderFunctions {...this.props}/>
        </FlexChild>
      </FlexGrid>
    )
  }
}


MobileOrderScreenRenderer.propTypes = {
  order: OrderPropTypes,
  selectedLine: PropTypes.object,
  selectedParent: PropTypes.object,
  skipAutoSelect: PropTypes.bool,
  onLineClick: PropTypes.func,
  customerName: PropTypes.string,
  selectedQty: PropTypes.number,
  onQtyChange: PropTypes.func,
  onUnselectLine: PropTypes.func,
  isModifiersDisplayed: PropTypes.bool,
  onSellItem: PropTypes.func,
  onSellOption: PropTypes.func,
  voidOrClearOption: PropTypes.func,
  onSellModifier: PropTypes.func,
  onAskBarcode: PropTypes.func,
  classes: PropTypes.object,
  workingMode: WorkingModePropTypes,
  onToggleSalePanel: PropTypes.func,
  isSalePanelVisible: PropTypes.bool,
  selectedTable: TablePropTypes,
  staticConfig: StaticConfigPropTypes,
  products: PropTypes.object,
  defaultNavigationIdx: PropTypes.number
}
