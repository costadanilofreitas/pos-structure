import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { FlexChild, FlexGrid, Image } from '3s-widgets'

import SaleType from '../../../../component/sale-type'
import OrderPropTypes from '../../../../../prop-types/OrderPropTypes'
import OrderFunctions from '../../../../component/order-functions'
import StaticConfigPropTypes from '../../../../../prop-types/StaticConfigPropTypes'
import OrderMenu from '../../../../component/order-menu'
import CustomSalePanel from '../../../../component/custom-sale-panel'
import { ImageContainer, SalePanelComponent } from '../StyledOrderScreen'
import ProductsContainer from '../common/ProductsContainer'
import ScreenOrientation from '../../../../../constants/ScreenOrientation'
import { ImageBackgroundOrderScreen } from '../../../../../constants/Images'


export default class TotemOrderScreenRenderer extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    const { classes, screenOrientation } = this.props
    const salePanelDirection = screenOrientation === ScreenOrientation.Portrait ? 'column' : 'row'
    const salePanelComponentsDirection = screenOrientation === ScreenOrientation.Landscape ? 'column' : 'row'

    return (
      <div style={{ backgroundColor: 'white', width: '100%', height: '100%', position: 'absolute' }}>
        <ImageContainer>
          <Image
            src={['./images/WelcomeScreenBackground.png', ImageBackgroundOrderScreen]}
            objectFit={'cover'}
            imageWidth={'100%'}
          />
        </ImageContainer>
        <div style={{ width: '100%', height: '100%', position: 'absolute' }}>
          <FlexGrid direction={`${salePanelDirection}-reverse`}>
            <SalePanelComponent
              size={1}
              style={screenOrientation === ScreenOrientation.Landscape ? { borderTop: 0 } : {}}
            >
              <FlexGrid direction={salePanelComponentsDirection}>
                <FlexChild size={2}>
                  <SaleType/>
                </FlexChild>
                <FlexChild size={14}>
                  {this.getCustomSalePanel()}
                </FlexChild>
                <FlexChild size={2}>
                  {this.getOrderFunctions()}
                </FlexChild>
              </FlexGrid>
            </SalePanelComponent>
            <FlexChild size={2}>
              <FlexGrid direction={'row'}>
                <FlexChild size={2} innerClassName={classes.menuTabsContainer}>
                  {this.getOrderMenu()}
                </FlexChild>
                <FlexChild
                  size={8}
                  innerClassName={classes.totemProductsContainer}
                  style={this.removeProductsContainerBorder(screenOrientation)}
                >
                  <ProductsContainer {...this.props}/>
                </FlexChild>
              </FlexGrid>
            </FlexChild>
          </FlexGrid>
        </div>
      </div>
    )
  }

  removeProductsContainerBorder(screenOrientation) {
    if (screenOrientation === ScreenOrientation.Landscape) {
      return { borderTop: 0, borderBottom: 0 }
    }

    return { borderTop: 0, borderBottom: 0, borderRight: 0 }
  }

  getOrderMenu() {
    const { rootGroups, selectedMenu, onMenuSelect, staticConfig } = this.props

    return (
      <OrderMenu
        selectedMenu={selectedMenu}
        groups={rootGroups}
        onMenuSelect={onMenuSelect}
        navigationOptions={staticConfig.totemConfigurations.navigation}
        direction={'column'}
      />
    )
  }

  getOrderFunctions() {
    const { isModifiersDisplayed, isCombo, onUnselectLine, screenOrientation } = this.props

    return (
      <OrderFunctions
        {...this.props}
        setSkipAutoSelect={(state) => this.setState({ skipAutoSelect: state })}
        modifierScreenOpen={isModifiersDisplayed && !isCombo}
        onCleanOrder={onUnselectLine}
        screenOrientation={screenOrientation}
      />
    )
  }

  getCustomSalePanel() {
    const { selectedLine, selectedParent, skipAutoSelect, onLineClick, order, onShowModifierScreen, onUnselectLine }
      = this.props
    return (
      <CustomSalePanel
        order={order}
        selectedLine={selectedLine}
        selectedParent={selectedParent}
        showSummary={true}
        showHeader={false}
        showSummaryChange={false}
        showSummaryDelivery={false}
        showSummaryDiscount={false}
        showSummaryDue={false}
        showSummaryService={false}
        showSummaryTax={false}
        showSummaryTip={false}
        showSummarySubtotal={false}
        showSummaryTotal={true}
        showHoldAndFire={true}
        showNotRequiredOptions={false}
        autoSelectLine={true}
        showFinishedSale={false}
        showDiscountedPrice={true}
        skipAutoSelect={skipAutoSelect}
        onLineClicked={onLineClick}
        onShowModifierScreen={onShowModifierScreen}
        onUnselectLine={onUnselectLine}
        showSaleItemOptions={true}
        saleSummaryStyle={'totemSaleSummaryLineRoot'}
        showCartMessage={true}
        styleOverflow={true}
      />
    )
  }
}

TotemOrderScreenRenderer.propTypes = {
  order: OrderPropTypes,
  selectedLine: PropTypes.object,
  selectedParent: PropTypes.object,
  skipAutoSelect: PropTypes.bool,
  onLineClick: PropTypes.func,
  onUnselectLine: PropTypes.func,
  isModifiersDisplayed: PropTypes.bool,
  isCombo: PropTypes.bool,
  onShowModifierScreen: PropTypes.func,
  rootGroups: PropTypes.oneOfType([PropTypes.array, PropTypes.object]),
  selectedMenu: PropTypes.number,
  onMenuSelect: PropTypes.func,
  staticConfig: StaticConfigPropTypes,
  classes: PropTypes.object,
  screenOrientation: PropTypes.number
}
