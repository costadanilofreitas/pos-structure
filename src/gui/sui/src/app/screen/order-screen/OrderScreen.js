import React, { Component } from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'

import { findClosestParent } from '3s-posui/utils'

import OrderPropTypes from '../../../prop-types/OrderPropTypes'
import OrderScreenRenderer from './order-screen-renderer'
import WorkingModePropTypes from '../../../prop-types/WorkingModePropTypes'
import { orderNotInState } from '../../util/orderValidator'
import OrderState from '../../model/OrderState'
import TablePropTypes from '../../../prop-types/TablePropTypes'
import MessageBusPropTypes from '../../../prop-types/MessageBusPropTypes'
import StaticConfigPropTypes from '../../../prop-types/StaticConfigPropTypes'
import { addAttributesToObject, getAllSaleTypes, getLastSaleLine } from '../../../util/orderUtil'
import { findSelectedFather, findSelectedLine, findSelectedParent, getOpenOption } from '../../util/saleLineUtil'
import { shallowIgnoreEquals } from '../../../util/renderUtil'


function getDefaultNavigation(defaultNavigation, navigation, saleType, defaultSaletype, workingMode) {
  let defaultNavigationIndex = -1
  if (saleType === 'DELIVERY' || defaultSaletype === 'DELIVERY') {
    const navIndex = navigation.findIndex(x => x.name.toUpperCase() === 'DELIVERY' || x.name.toUpperCase() === 'DL')
    defaultNavigationIndex = navIndex
  } else if (workingMode.podType === 'TT') {
    const navIndex = navigation.findIndex(x => x.name.toUpperCase() === 'TOTEM' || x.name.toUpperCase() === 'TT')
    defaultNavigationIndex = navIndex
  } else {
    if (defaultNavigation !== '') {
      defaultNavigationIndex = navigation.findIndex(x => x.name === defaultNavigation)
    }
    if (defaultNavigationIndex === -1) {
      defaultNavigationIndex = navigation.findIndex(x => x.name.toUpperCase() === 'FC')
    }
  }

  return defaultNavigationIndex
}

function getNavigationIndex(defaultNavigation, nextProps, defaultSaletype) {
  let navigationIndex = 0
  const defaultNavigationIndex = getDefaultNavigation(defaultNavigation, nextProps.navigation,
    nextProps.saleType, defaultSaletype, nextProps.workingMode)
  if (defaultNavigationIndex != null) {
    navigationIndex = defaultNavigationIndex
  }
  return navigationIndex
}

function notAllCommentsEqual(currentLineComments, nextLineComments) {
  return !currentLineComments.sort().every(function (value, index) {
    return value === nextLineComments.sort()[index]
  })
}

function selectedLineCommentsChanged(currentStateLine, nextStateLine) {
  const currentLineComments = currentStateLine != null ? currentStateLine.Comment : []
  const nextLineComments = nextStateLine != null ? nextStateLine.Comment : []
  if (currentLineComments.length !== nextLineComments.length) {
    return true
  }

  return notAllCommentsEqual(currentLineComments, nextLineComments)
}

export default class OrderScreen extends Component {
  constructor(props) {
    super(props)

    this.specialMenuList = this.getSpecialConfigMenu()
    if (this.props.selectedTable && this.props.selectedTable.specialCatalog) {
      this.tableCatalog = this.props.selectedTable.specialCatalog
    } else {
      this.tableCatalog = ''
    }
    let listSpecialCatalog = ''
    if (this.tableCatalog) {
      if (this.props.specialCatalog) {
        listSpecialCatalog = this.props.specialCatalog.concat('.')
      }
      listSpecialCatalog = listSpecialCatalog.concat(this.tableCatalog)
    } else {
      listSpecialCatalog = this.props.specialCatalog
    }
    this.specialCatalogs = listSpecialCatalog

    this.state = {
      navigationIdx: 1,
      oldLines: 0,
      orderLastTimestamp: 0,
      selectedParent: null,
      selectedLine: null,
      userClicked: false,
      skipAutoSelect: false,
      selectedSeat: 1,
      selectedQty: 1,
      isModifiersDisplayed: false,
      specialCatalog: false,
      selectedMenu: 0,
      isSalePanelVisible: false,
      isSearchMobile: false,
      showBarcodeScreen: false,
      showSearchScreen: false
    }

    this.handleLineClicked = this.handleLineClicked.bind(this)
    this.handleOnSeatChange = this.handleOnSeatChange.bind(this)
    this.handleOnUnselectLine = this.handleOnUnselectLine.bind(this)
    this.handleOnShowModifierScreen = this.handleOnShowModifierScreen.bind(this)
    this.handleSellItem = this.handleSellItem.bind(this)
    this.handleOnSellOption = this.handleOnSellOption.bind(this)
    this.handleOnSellModifier = this.handleOnSellModifier.bind(this)
    this.voidOrClearOption = this.voidOrClearOption.bind(this)

    this.handleOnMenuSelect = this.handleOnMenuSelect.bind(this)
    this.handleOnQtyChange = this.handleOnQtyChange.bind(this)
    this.hasModifiers = this.hasModifiers.bind(this)
    this.isOptionOrChoice = this.isOptionOrChoice.bind(this)
    this.handleOnToggleSalePanel = this.handleOnToggleSalePanel.bind(this)
    this.onChangeSearchMobile = this.onChangeSearchMobile.bind(this)
    this.handleOnAskBarcode = this.handleOnAskBarcode.bind(this)
    this.handleOnSellByBarcode = this.handleOnSellByBarcode.bind(this)

    const sellByBarcodeFunction = this.handleOnSellByBarcode
    window.scanner = {
      sellByBarcode: function (barcode) {
        sellByBarcodeFunction(null, barcode)
      }
    }
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    let { selectedLine, oldLines, orderLastTimestamp } = prevState
    const { staticConfig } = nextProps
    const availableSaleTypes = getAllSaleTypes(staticConfig.availableSaleTypes)
    const defaultSaletype = availableSaleTypes != null ? availableSaleTypes[0] : null
    const defaultNavigation = staticConfig.posNavigation

    let selectedMenu = prevState.selectedMenu

    const navigationIndex = getNavigationIndex(defaultNavigation, nextProps, defaultSaletype)
    if (navigationIndex !== prevState.navigationIdx) {
      selectedMenu = 0
    }

    const nextOrder = nextProps.order || {}
    const newLines = _.reduce(nextOrder.SaleLine, (sum, order) => {
      return sum + ((parseFloat(order.level) === 0 && parseFloat(order.qty) > 0) ? 1 : 0)
    }, 0)

    let newSelectedLine
    let changeModifierDisplayed = nextProps.mobile && prevState.isModifiersDisplayed

    if (oldLines < newLines) {
      selectedLine = getLastSaleLine(nextProps.order)
      if (selectedLine != null) {
        newSelectedLine = addAttributesToObject(selectedLine)
        let newSelectedParent = findSelectedParent(nextOrder, newSelectedLine)
        newSelectedParent = findSelectedLine(nextOrder, newSelectedParent)

        return {
          navigationIdx: navigationIndex,
          selectedMenu: selectedMenu,
          oldLines: newLines,
          orderLastTimestamp: nextProps.orderLastTimestamp,
          selectedLine: newSelectedLine,
          selectedParent: newSelectedParent
        }
      }
    } else if (orderLastTimestamp !== nextProps.orderLastTimestamp) {
      const openOption = getOpenOption(nextOrder.SaleLine)

      let isModifiersDisplayed
      if (openOption && parseFloat(openOption.minQty) > 0) {
        newSelectedLine = openOption
        isModifiersDisplayed = true
      } else {
        newSelectedLine = findSelectedLine(nextOrder, selectedLine)
        if (newSelectedLine != null && newSelectedLine.qty === '0' && newSelectedLine.itemType !== 'OPTION') {
          newSelectedLine = findSelectedFather(nextOrder, selectedLine)
        }

        if (newSelectedLine != null && newSelectedLine.itemType === 'OPTION') {
          isModifiersDisplayed = parseFloat(newSelectedLine.chosenQty) < parseFloat(newSelectedLine.maxQty)
        } else if (selectedLineCommentsChanged(newSelectedLine, prevState.selectedLine)) {
          isModifiersDisplayed = false
          changeModifierDisplayed = false
        } else {
          isModifiersDisplayed = newSelectedLine != null ? prevState.isModifiersDisplayed : false
        }
      }

      if (newSelectedLine != null) {
        newSelectedLine = findClosestParent(nextOrder, newSelectedLine)
        let newSelectedParent = findSelectedParent(nextOrder, newSelectedLine)
        newSelectedParent = findSelectedLine(nextOrder, newSelectedParent)

        return {
          navigationIdx: navigationIndex,
          selectedMenu: selectedMenu,
          oldLines: newLines,
          orderLastTimestamp: nextProps.orderLastTimestamp,
          userClicked: false,
          isModifiersDisplayed: changeModifierDisplayed ? prevState.isModifiersDisplayed : isModifiersDisplayed,
          selectedLine: newSelectedLine,
          selectedParent: newSelectedParent,
          skipAutoSelect: true,
          selectedQty: 1
        }
      }
    }

    return {
      isModifiersDisplayed: nextOrder.state !== 'IN_PROGRESS' ? false : prevState.isModifiersDisplayed,
      navigationIdx: navigationIndex,
      selectedMenu: selectedMenu,
      oldLines: newLines,
      orderLastTimestamp: nextProps.orderLastTimestamp
    }
  }

  shouldComponentUpdate(nextProps, nextState) {
    const changedState = !shallowIgnoreEquals(this.state, nextState)
    const orderUpdated = this.props.orderLastTimestamp !== nextProps.orderLastTimestamp

    if (nextProps.selectedTable !== this.props.selectedTable) {
      return true
    }

    if (nextState.navigationIdx !== this.state.navigationIdx) {
      this.groupsByTab = null
      return true
    }

    if (nextProps.actionRunning.busy === true) {
      if (nextState.selectedLine !== this.state.selectedLine || nextState.selectedLine == null) {
        return true
      } else if (nextState.userClicked !== true) {
        return false
      }
    }

    if (nextProps.screenOrientation !== this.props.screenOrientation) {
      return true
    }

    return orderUpdated || changedState
  }

  getSearchNavigationIndex(navigation) {
    return navigation.findIndex(x => x.name === 'SEARCH')
  }

  render() {
    const { staticConfig, navigation, workingMode } = this.props
    const isCombo = (this.state.selectedLine || {}).itemType === 'COMBO'
    const newSelectedLine = findSelectedLine(this.props.order, this.state.selectedLine)
    const newSelectedParent = findSelectedLine(this.props.order, this.state.selectedParent)
    const availableSaleTypes = getAllSaleTypes(staticConfig.availableSaleTypes)
    const defaultSaletype = availableSaleTypes != null ? availableSaleTypes[0] : null

    if (this.groupsByTab == null || _.isEmpty(this.groupsByTab)) {
      this.groupsByTab = this.getGroupsByTab(this.props, this.specialMenuList, this.specialCatalogs)
    }

    let showSearchScreen = this.state.showSearchScreen
    let showBarcodeScreen = this.state.showBarcodeScreen

    if (_.isEmpty(this.groupsByTab) && (!this.state.showBarcodeScreen && !this.state.showSearchScreen) &&
      workingMode.podType !== 'TT') {
      if (staticConfig.navigationOptions.showBarcodeScreen) {
        showSearchScreen = true
      } else if (staticConfig.navigationOptions.showSearchScreen) {
        showBarcodeScreen = true
      }
    }

    const navigationGroups = showBarcodeScreen ? [] : (this.groupsByTab[this.state.selectedMenu] || {}).groups

    return (
      <OrderScreenRenderer
        selectedLine={newSelectedLine}
        selectedParent={newSelectedParent}
        skipAutoSelect={this.state.skipAutoSelect}
        onLineClick={this.handleLineClicked}
        order={this.props.order}
        customerName={this.getCustomerName()}
        rootGroups={this.groupsByTab}
        groups={navigationGroups}
        selectedMenu={this.state.selectedMenu}
        onMenuSelect={this.handleOnMenuSelect}
        showSearch={showSearchScreen && !this.state.isModifiersDisplayed}
        showBarcodeScreen={showBarcodeScreen}
        saleType={this.props.saleType}
        selectedTable={this.props.selectedTable}
        showSearchMobile={this.state.isSearchMobile}
        changeSearchMobile={this.onChangeSearchMobile}
        onSellItem={this.handleSellItem}
        onSellOption={this.handleOnSellOption}
        onSellModifier={this.handleOnSellModifier}
        voidOrClearOption={this.voidOrClearOption}
        selectedSeat={this.state.selectedSeat}
        onSeatChange={this.handleOnSeatChange}
        selectedQty={this.state.selectedQty}
        onQtyChange={this.handleOnQtyChange}
        onUnselectLine={this.handleOnUnselectLine}
        isModifiersDisplayed={!showBarcodeScreen && this.state.isModifiersDisplayed}
        isCombo={isCombo}
        onShowModifierScreen={this.handleOnShowModifierScreen}
        workingMode={this.props.workingMode}
        isSalePanelVisible={this.state.isSalePanelVisible}
        onToggleSalePanel={this.handleOnToggleSalePanel}
        staticConfig={this.props.staticConfig}
        onAskBarcode={this.handleOnAskBarcode}
        handleOnSellByBarcode={this.handleOnSellByBarcode}
        screenOrientation={this.props.screenOrientation}
        searchNavigation={this.getSearchNavigationIndex(this.props.navigation) !== -1}
        defaultNavigationIdx={getNavigationIndex(staticConfig.posNavigation, this.props, defaultSaletype)}
        searchScreenItems={this.getSearchScreenItems(navigation)}
      />
    )
  }

  getSearchScreenItems(navigation) {
    if (navigation[this.getSearchNavigationIndex(navigation)] == null) {
      return []
    }

    return navigation[this.getSearchNavigationIndex(navigation)].items
  }

  onChangeSearchMobile() {
    this.setState({ isSearchMobile: !this.state.isSearchMobile })
  }

  handleLineClicked(line, parentLine, userClicked, autoOpenModifiers) {
    const { order } = this.props
    const newSelectedLine = findClosestParent(order, line)

    let newShowModifierScreen = false
    const isOptionOrChoice = this.isOptionOrChoice(newSelectedLine)
    if (isOptionOrChoice === true || autoOpenModifiers === true) {
      newShowModifierScreen = true
    }

    const selectedLine = findSelectedLine(this.props.order, newSelectedLine)
    const selectedParent = findSelectedLine(this.props.order, parentLine)

    this.setState({
      userClicked: userClicked,
      selectedLine: selectedLine,
      selectedParent: selectedParent,
      skipAutoSelect: userClicked,
      isModifiersDisplayed: this.props.mobile ? this.state.isModifiersDisplayed : newShowModifierScreen
    })
  }

  handleOnSeatChange(newSeat) {
    this.setState({ selectedSeat: newSeat })
  }

  handleOnUnselectLine() {
    this.setState({
      selectedLine: null,
      selectedParent: null,
      skipAutoSelect: true,
      userClicked: true,
      isModifiersDisplayed: false
    })
  }

  handleOnShowModifierScreen() {
    this.setState({ isModifiersDisplayed: !this.state.isModifiersDisplayed, isSalePanelVisible: false })
  }

  handleSellItem(item) {
    const saleType = this.props.saleType
    const { selectedLine } = this.state
    const qty = this.state.selectedQty
    const line = selectedLine ? selectedLine.lineNumber : ''
    const seat = this.state.selectedSeat
    const partCode = item.product_code != null ? item.product_code : item.rowData.plu

    this.props.msgBus.syncAction('doCompleteOption',
      '1',
      partCode,
      qty,
      line,
      '',
      saleType,
      '',
      this.props.selectedTable != null ? seat : '',
      this.specialCatalogs)
  }

  handleOnSellOption(item, itemId, subst, autoExitModScreen, qty, comment) {
    const { selectedLine } = this.state
    const { partCode } = selectedLine || {}
    const level = parseInt((selectedLine || {}).level || '0', 10)
    const sellLineNumber = selectedLine.lineNumber
    const sellQty = qty == null ? '1' : qty

    let fullItemId = ''
    if (level > 0 && subst) {
      if (itemId && partCode) {
        fullItemId = `${itemId}${subst}`
      }
    }

    this.props.msgBus.syncAction(
      'doCompleteOption',
      itemId,
      item.product_code,
      sellQty,
      sellLineNumber,
      '',
      '',
      fullItemId,
      '',
      '',
      comment)
  }

  voidOrClearOption(selectedLine, allItems) {
    const level = parseInt((selectedLine || {}).level || '0', 10)
    const { itemId, partCode, lineNumber } = selectedLine || {}

    if (level > 0) {
      let fullItemId = ''
      if (itemId && partCode) {
        fullItemId = `${itemId}.${partCode}`
      }
      this.props.msgBus.syncAction(
        'doClearOptionItem',
        lineNumber,
        fullItemId,
        '',
        allItems === true ? 'true' : 'false'
      )
    }
  }

  handleOnSellModifier(item, selectedLine, modType, modQty) {
    let qty

    if (modQty == null) {
      qty = (modType === 'WITHOUT') || (modType === '$WITHOUT') ? 0 : 1
      qty = (item.selected && modType === 'TOGGLE') ? 0 : qty
    } else {
      qty = modQty
    }

    this.props.msgBus.syncAction(
      'doModifier',
      `${selectedLine.itemId}.${selectedLine.partCode}`,
      selectedLine.level,
      item.product_code,
      qty,
      selectedLine.lineNumber,
      modType == null ? '' : modType
    )
  }

  handleOnAskBarcode() {
    this.props.msgBus.syncAction('do_ask_barcode')
  }

  handleOnMenuSelect(menu, showBarcodeScreen, showSearchScreen) {
    this.setState({
      isModifiersDisplayed: false,
      selectedMenu: menu,
      skipAutoSelect: true,
      showBarcodeScreen,
      showSearchScreen
    })
  }

  handleOnQtyChange(qty) {
    this.setState({
      userClicked: true,
      skipAutoSelect: true,
      selectedQty: qty
    })
  }

  handleOnToggleSalePanel() {
    this.setState({ isSalePanelVisible: !this.state.isSalePanelVisible })
  }

  handleOnSellByBarcode(typedBarcode = null, scannedBarcode = null, callback = null) {
    if (this.props.dialogs.length > 0) {
      return
    }

    if (typedBarcode || scannedBarcode) {
      const barcode = typedBarcode != null ? typedBarcode : scannedBarcode
      this.props.msgBus.syncAction('do_sell_product_by_barcode', barcode, true, this.state.selectedQty)
        .then(response => {
          if (callback != null) {
            callback(response)
          }
        })
    }
  }

  isOptionOrChoice(selectedLine) {
    const { order } = this.props
    if (selectedLine.itemType === 'OPTION') {
      return true
    }

    for (let i = 0; i < (order.SaleLine || {}).length; i++) {
      const saleLine = (order.SaleLine[i] || {})['@attributes'] || {}
      const fatherLevel = parseInt(selectedLine.level, 10) - 1
      if (
        parseInt(saleLine.level, 10) === fatherLevel &&
        saleLine.lineNumber === selectedLine.lineNumber &&
        saleLine.partCode === selectedLine.itemId.split('.').pop()) {
        return (saleLine.itemType === 'OPTION')
      }
    }
    return false
  }

  getCustomerName() {
    if (orderNotInState(this.props.order, OrderState.InProgress, OrderState.Totaled)) {
      return null
    }

    const customerName = (this.props.order.CustomOrderProperties || {}).CUSTOMER_NAME
    if (!customerName) {
      return null
    }
    return customerName
  }

  hasModifiers(selectedLine) {
    const { modifiers } = this.props

    if (selectedLine.itemType === 'OPTION') {
      return false
    }

    if (selectedLine.partCode in modifiers.modifiers) {
      const mods = modifiers.modifiers[selectedLine.partCode].parts
      if (_.find(mods, { 'isOption': false }) != null) {
        return true
      }
    }

    return false
  }

  getSpecialConfigMenu() {
    const specialMenuList = {}
    const { staticConfig } = this.props
    if (staticConfig) {
      _.forEach(staticConfig.specialMenus, (menu) => {
        const menuString = menu.split(':')
        const key = menuString[1]
        const value = menuString[0]
        specialMenuList[key] = { title: value }
      })
    }
    return specialMenuList
  }

  getGroupsByTab(props, specialMenuList, specialCatalogs) {
    const { navigation, staticConfig, products } = props
    const showRupturedProducts = staticConfig.showRupturedProducts
    const rupturedProducts = Object.values(products).filter(p => p.ruptured)
    const groupsByTab = {}
    const menuList = specialMenuList

    let groups = (navigation[this.state.navigationIdx] || {}).groups || []
    if (groups.length === 0 && navigation[this.state.navigationIdx] !== undefined) {
      groups = [navigation[this.state.navigationIdx]]
    }

    let catalogs = ''
    if (specialCatalogs) {
      catalogs = specialCatalogs.split('.')
    }
    _.forEach(catalogs, (catalog) => {
      if (catalog in menuList) {
        menuList[catalog].title = null
      }
    })
    let idx = 0
    _.forEach(groups, (group) => {
      let hiddenClass = false
      _.forEach(menuList, specialMenu => {
        if (group.text === specialMenu.title) {
          hiddenClass = true
        }
      })
      const newGroup = _.cloneDeep(group)
      if (!hiddenClass) {
        if (((group || {}).items || []).length > 0) {
          // this tab does not have sub-categories, but it has items, so handle them as a single
          // sub-category with no title
          newGroup.groups = [_.cloneDeep(newGroup)]
          newGroup.groups[0].text = null
        }
        if (((group || {}).groups || []).length > 0) {
          // group names should not have more than 20 characters
          newGroup.groups = _.map(group.groups, (childGroup) => {
            return { ...childGroup, text: (childGroup.text || '').substring(0, 20) }
          })
        }
        groupsByTab[idx] = showRupturedProducts ? newGroup : this.removeRupturedProducts(newGroup, rupturedProducts)
        idx += 1
      }
    })
    return groupsByTab
  }

  removeRupturedProducts(group, rupturedProducts) {
    if (group.groups.length === 0) {
      return
    }

    _.forEach(group.groups, (g) => {
      g.items = g.items.filter(i => !rupturedProducts.some(p => p.product_code === i.product_code))
      this.removeRupturedProducts(g, rupturedProducts)
    })

    return group
  }
}

const itemPropTypes = PropTypes.shape({
  text: PropTypes.string.isRequired,
  product_code: PropTypes.string.isRequired,
  bgColor: PropTypes.string.isRequired
})

const groupPropTypes = PropTypes.shape({
  text: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  items: PropTypes.arrayOf(itemPropTypes)
})

groupPropTypes.groups = PropTypes.arrayOf(groupPropTypes)

OrderScreen.propTypes = {
  actionRunning: PropTypes.object,
  order: OrderPropTypes,
  mobile: PropTypes.bool,
  workingMode: WorkingModePropTypes,
  specialCatalog: PropTypes.string,
  saleType: PropTypes.string,
  staticConfig: StaticConfigPropTypes,
  modifiers: PropTypes.object,
  orderLastTimestamp: PropTypes.number,
  selectedTable: TablePropTypes,
  msgBus: MessageBusPropTypes,
  dialogs: PropTypes.array,
  deviceType: PropTypes.number,
  screenOrientation: PropTypes.number,
  products: PropTypes.object,
  navigation: PropTypes.array
}
