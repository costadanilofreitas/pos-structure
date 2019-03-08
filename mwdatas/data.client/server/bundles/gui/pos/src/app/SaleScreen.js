import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Button } from 'posui/button'
import { NavigationGrid, ButtonGrid, SaleTypeSelector } from 'posui/widgets'
import { SalePanel } from 'posui/sale-panel'
import { getFirstOpenOption, findClosestParent } from 'posui/utils'
import { I18N } from 'posui/core'
import injectSheet, { jss } from 'react-jss'
import _ from 'lodash'
import SearchIcon from '../icons/Search'
import QtyButtons from './QtyButtons'
import OrderFunctions from './OrderFunctions'
import Options from './Options'
import Modifiers from './Modifiers'
import ProductSearch from './ProductSearch'


jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = (theme) => ({
  containerStyle: {
    display: 'flex',
    flexDirection: 'column',
    width: '100%',
    height: '100%',
    position: 'absolute'
  },
  absoluteWrapper: {
    position: 'absolute',
    width: '100%',
    height: '100%'
  },
  tabContainerStyle: {
    flexGrow: 6,
    flexShrink: 0,
    flexBasis: 0,
    display: 'flex',
    width: '100%',
    height: '100%',
    position: 'relative'
  },
  tabButtonStyle: {
    flexGrow: 1,
    flexShrink: 0,
    flexBasis: 0,
    padding: '1px'
  },
  saleContainerStyle: {
    flexGrow: 94,
    flexShrink: 0,
    flexBasis: 0,
    display: 'flex',
    width: '100%',
    height: '100%',
    position: 'relative',
    padding: '0.5vh 0.5%',
    boxSizing: 'border-box'
  },
  leftPanel: {
    flexGrow: 30,
    flexShrink: 0,
    flexBasis: 0,
    position: 'relative'
  },
  leftFlexContainer: {
    display: 'flex',
    flexDirection: 'column',
    width: '100%',
    height: '100%',
    position: 'absolute'
  },
  saleTypeBox: {
    position: 'relative',
    flexGrow: 5,
    flexShrink: 0,
    flexBasis: 0,
    margin: '0.2vh 0 0.5vh',
    minHeight: '4.5vh'
  },
  salePanelBox: {
    flexGrow: 80,
    flexShrink: 0,
    flexBasis: 0,
    position: 'relative',
    marginBottom: '0.5vh'
  },
  salePanel: {
    backgroundColor: 'white'
  },
  quantityBox: {
    flexGrow: 6,
    flexShrink: 0,
    flexBasis: 0,
    position: 'relative',
    margin: '0 0.5%'
  },
  rightPanel: {
    flexGrow: 66,
    flexShrink: 0,
    flexBasis: 0,
    position: 'relative'
  },
  customerNameLine: {
    fontSize: '1.5vh',
    paddingTop: '0.4vh'
  },
  wrapper: {
    display: 'flex',
    position: 'absolute',
    width: '100%',
    height: '100%',
    flexWrap: 'wrap',
    flexDirection: 'row'
  },
  container: {
    flexGrow: 85,
    flexShrink: 0,
    flexBasis: '85%',
    position: 'relative',
    height: '92%'
  },
  grid: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    backgroundColor: 'white',
    padding: '1vh 1%',
    boxSizing: 'border-box'
  },
  tabs: {
    flexGrow: 15,
    flexShrink: 0,
    flexBasis: '15%',
    position: 'relative',
    height: '92%'
  },
  submenu: {
    ...(theme.submenu || {})
  },
  submenuActive: {
    ...(theme.submenuActive || {})
  },
  submenuNotLast: {
    ...(theme.submenuNotLast || {})
  },
  modifierButtons: {
    height: '10%',
    position: 'relative',
    flexGrow: 100,
    flexBasis: '100%'
  }
})

class SaleScreen extends PureComponent {

  constructor(props) {
    super(props)
    this.NAVIGATION_MENU = 1
    this.state = {
      showModifierScreen: false,
      selectedLine: {},
      selectedParent: {},
      selectedTabIdx: 0,
      selectedQty: 1,
      skipAutoSelect: false
    }
    const { submenu, submenuActive } = this.getSubmenu(props)
    this.submenu = submenu
    this.submenuActive = submenuActive
    this.groupsByTab = this.getGroupsByTab(props)
    const commonStyle = {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: '1.8vh',
      height: '5vh',
      fontWeight: 'bold'
    }
    this.styleTitle = {
      ...commonStyle,
      color: 'black'
    }
    this.styleTitleDark = {
      ...commonStyle,
      color: '#eeeeee'
    }
  }

  handleSubmenuClicked = (idx) => () => {
    this.setState({
      showModifierScreen: false,
      selectedTabIdx: idx,
      skipAutoSelect: true
    })
  }

  getSubmenu(props) {
    const { classes, navigation, themeName } = props
    const tabs = (navigation[this.NAVIGATION_MENU] || {}).groups || []
    const submenu = {}
    const submenuActive = {}
    _.forEach(tabs, (tab, idx) => {
      submenu[idx] = (
        <Button
          key={`${idx}_inactive_${themeName}`}
          className={`${classes.tabButtonStyle} ${classes.submenu} ${classes.submenuNotLast}`}
          onClick={this.handleSubmenuClicked(idx)}
          blockOnActionRunning={true}
        >{tab.text}</Button>
      )
      submenuActive[idx] = (
        <Button
          key={`${idx}_active_${themeName}`}
          className={`${classes.tabButtonStyle} ${classes.submenu} ${classes.submenuNotLast} ${classes.submenuActive}`}
          onClick={this.handleSubmenuClicked(idx)}
          blockOnActionRunning={true}
        >{tab.text}</Button>
      )
    })
    const idx = tabs.length
    submenu[idx] = (
      <Button
        key={`${idx}_inactive_${themeName}`}
        className={`${classes.tabButtonStyle} ${classes.submenu}`}
        onClick={this.handleSubmenuClicked(idx)}
          blockOnActionRunning={true}
      ><SearchIcon /></Button>
    )
    submenuActive[idx] = (
      <Button
        key={`${idx}_active_${themeName}`}
        className={`${classes.tabButtonStyle} ${classes.submenu} ${classes.submenuActive}`}
        onClick={this.handleSubmenuClicked(idx)}
          blockOnActionRunning={true}
      ><SearchIcon /></Button>
    )
    return { submenu, submenuActive }
  }

  renderTabs() {
    const { classes, order } = this.props
    const { selectedLine } = this.state
    const { lineNumber } = selectedLine || {}

    // collect lines from current order that should be displayed as tabs, either open options
    // or already selected children
    const tabSaleLines = []
    const minLevel = 1  // note: we might need a maxLevel too in case of options with sub-options
    let lastOption = null
    _.forEach(order.SaleLine || [], (line) => {
      const saleLine = line['@attributes'] || {}
      const type = saleLine.itemType
      const isOption = type === 'OPTION'
      const isProduct = type === 'PRODUCT'
      const qty = parseInt(saleLine.qty, 10)
      const level = parseInt(saleLine.level, 10)
      const chosenQty = parseInt(saleLine.chosenQty, 10) || 0
      let isOptionChild = false
      if (isOption) {
        lastOption = `${saleLine.itemId}.${saleLine.partCode}`
      } else if (saleLine.itemId === lastOption) {
        isOptionChild = true
      }
      if (saleLine.lineNumber === lineNumber && level >= minLevel &&
         ((isOption && chosenQty < qty) ||
          (isOptionChild && qty > 0) ||
          (isProduct && qty > 0))) {
        tabSaleLines.push(saleLine)
      }
    })

    const tabButtons = {}
    _.forEach(tabSaleLines, (saleLine, idx) => {
      const selected = _.isEqual(saleLine, selectedLine)
      const clazz = ((selected) ? 'modtab-active' : 'modtab-inactive')
      tabButtons[idx] = (
        <Button
          key={`${order.orderId}_${saleLine.lineNumber}_${idx}_${selected}`}
          className={`${classes.tabButtonStyle} modtab ${clazz}`}
          onClick={() => this.setState({ selectedLine: saleLine })}
          blockOnActionRunning={true}
        >
          {saleLine.productName}
        </Button>
      )
    })
    return (
      <ButtonGrid
        direction="row"
        cols={1}
        rows={10}
        buttons={tabButtons}
        styleCell={{ paddingTop: '1vh' }}
      />
    )
  }

  handleChangeQty = (qty) => {
    this.setState({
      skipAutoSelect: true,
      selectedQty: qty
    })
  }

  getGroupsByTab = (props) => {
    const { navigation } = props
    const groups = (navigation[this.NAVIGATION_MENU] || {}).groups || []
    const groupsByTab = {}

    _.forEach(groups, (group, idx) => {
      let tempGroups = []

      _.forEach(group.groups, (group) => {
        if ((group.text || '').length > 20) {
          group.text = group.text.substring(0, 20)
        }
      })

      if ((group.items || []).length > 0) {
        // this tab does not have sub-categories, but it has items, so handle them as a single
        // sub-category with no title
        tempGroups = [{
          items: group.items,
          name: group.name,
          text: null,
          classes: group.classes || []
        }]
      }
      if ((group.groups || []).length > 0) {
        tempGroups = [...tempGroups, ...group.groups]
      }
      groupsByTab[idx] = tempGroups
    })
    return groupsByTab
  }

  sellItem = (item) => {
    const { selectedLine } = this.state
    const qty = this.state.selectedQty
    this.setState({ selectedQty: 1, skipAutoSelect: false })
    return ['doCompleteOption', this.NAVIGATION_MENU, item.plu, qty, selectedLine.lineNumber]
  }

  sellOption = (item, itemId) => {
    const { selectedLine } = this.state
    const qty = this.state.selectedQty
    this.setState({ selectedQty: 1, skipAutoSelect: false })
    return ['doOption', itemId, item.plu, qty, selectedLine.lineNumber]
  }

  sellModifier = (item, selectedLine, modType) => {
    const qty = (modType === 'EXTRA') ? 2 : 1
    return [
      'doModifier',
      `${selectedLine.itemId}.${selectedLine.partCode}`,
      selectedLine.level,
      item.plu,
      (item.selected && modType === 'TOGGLE') ? 0 : qty,
      selectedLine.lineNumber,
      modType
    ]
  }

  handleHeaderRendered = () => {
    const { classes, order } = this.props
    const customerName = (order.CustomOrderProperties || {}).CUSTOMER_NAME
    if (!customerName) {
      return null
    }
    return (
      <div className={classes.customerNameLine}>Customer name: <em>{customerName}</em></div>
    )
  }

  handleLineClicked = (line, parentLine, userClicked) => {
    const { order } = this.props
    const { showModifierScreen } = this.state
    const attributes = order['@attributes'] || {}
    const inProgress = _.includes(['IN_PROGRESS', 'TOTALED'], attributes.state)
    if (!inProgress && userClicked) {
      this.setState({
        selectedLine: null,
        selectedParent: null,
        skipAutoSelect: true
      })
      return
    }
    let newShowModifierScreen = showModifierScreen
    if (line.itemType === 'OPTION') {
      newShowModifierScreen = true
    }
    this.setState({
      selectedLine: findClosestParent(order, line),
      selectedParent: parentLine,
      skipAutoSelect: userClicked,
      showModifierScreen: newShowModifierScreen
    })
  }

  componentWillReceiveProps(nextProps) {
    const { selectedLine } = this.state

    if (this.props.navigation !== nextProps.navigation) {
      const { submenu, submenuActive } = this.getSubmenu(nextProps)
      this.submenu = submenu
      this.submenuActive = submenuActive
      this.groupsByTab = this.getGroupsByTab(nextProps)
    }
    if (this.props.orderLastTimestamp !== nextProps.orderLastTimestamp && selectedLine !== null) {
      const nextOrder = nextProps.order || {}
      let newSelectedLine = selectedLine
      const lastModifiedLine = (nextOrder['@attributes'] || {}).lastModifiedLine
      if (lastModifiedLine) {
        const line = getFirstOpenOption(nextOrder.SaleLine, lastModifiedLine)
        if (line) {
          newSelectedLine = line
        }
      }
      // check if selected line is a modifier and try to find closest parent
      const nextParent = findClosestParent(nextOrder, newSelectedLine)
      if (!_.isEqual(nextParent, selectedLine)) {
        this.setState({
          selectedLine: nextParent,
          showModifierScreen: true
        })
      }
    }
  }

  render() {
    const { classes, order, modifiers, custom, themeName, navigation } = this.props
    const { skipAutoSelect, selectedQty, selectedLine, selectedParent, showModifierScreen,
      selectedTabIdx } = this.state
    const attributes = order['@attributes'] || {}
    const inProgress = _.includes(['IN_PROGRESS', 'TOTALED'], attributes.state)
    const isCombo = (selectedLine || {}).itemType === 'COMBO'
    const isOption = (selectedLine || {}).itemType === 'OPTION'
    const submenu = { ...this.submenu, [selectedTabIdx]: this.submenuActive[selectedTabIdx] }
    const isSearch = ((navigation[1] || {}).groups || []).length === selectedTabIdx

    const modifierButtons = {
      3: <Button
          rounded={true}
          className="function-btn"
          onClick={() => this.setState({ showModifierScreen: false })}
          blockOnActionRunning={true}
      >
        <I18N id="$OK" defaultMessage="OK"/>
      </Button>
    }

    return (
      <div className={classes.containerStyle}>
        <div className={classes.tabContainerStyle}>
          <ButtonGrid
            direction="row"
            cols={_.size(submenu)}
            rows={1}
            buttons={submenu}
          />
        </div>
        <div className={classes.saleContainerStyle} style={{ flexDirection: (custom.MIRROR_SCREEN === 'true') ? 'row-reverse' : 'row' }}>
          <div className={classes.leftPanel}>
            <div className={classes.leftFlexContainer}>
              <div className={classes.saleTypeBox}>
                <div className={classes.absoluteWrapper}>
                  <SaleTypeSelector rounded={true} border={true} direction="row" />
                </div>
              </div>
              <div className={classes.salePanelBox}>
                <div className={classes.absoluteWrapper}>
                  <SalePanel
                    className={classes.salePanel}
                    order={order}
                    selectedLine={selectedLine}
                    selectedParent={selectedParent}
                    showSummary={attributes.state === 'IN_PROGRESS'}
                    showSummaryChange={false}
                    showSummaryDelivery={false}
                    showSummaryDiscount={false}
                    showSummaryDue={false}
                    showSummaryService={false}
                    showSummaryTax={false}
                    showSummaryTip={false}
                    showSummaryTotal={false}
                    showSummaryTotalAfterDiscount={false}
                    showFinishedSale={false}
                    autoSelectLine={true}
                    skipAutoSelect={skipAutoSelect}
                    onLineClicked={this.handleLineClicked}
                    onHeaderRendered={this.handleHeaderRendered}
                  />
                </div>
              </div>
              <OrderFunctions
                selectedLine={selectedLine}
                inProgress={inProgress}
                selectedQty={selectedQty}
                onUnselectLine={() => {
                  this.setState({
                    selectedLine: null,
                    selectedParent: null,
                    skipAutoSelect: true,
                    showModifierScreen: false
                  })
                }}
                modifierScreenOpen={!isCombo && showModifierScreen}
                onShowModifierScreen={() => {
                  this.setState({
                    showModifierScreen: !showModifierScreen
                  })
                }}
                order={order}
              />
            </div>
          </div>
          <div className={classes.quantityBox}>
            <QtyButtons
              value={selectedQty}
              onChange={this.handleChangeQty}
            />
          </div>
          <div className={classes.rightPanel}>
            {!isSearch && (!isCombo && showModifierScreen && inProgress) &&
              <div className={classes.wrapper}>
                <div className={classes.container}>
                  <div className={classes.grid}>
                    {(!isOption) &&
                      <Modifiers
                        order={order}
                        modifiers={modifiers}
                        saleLine={selectedLine}
                        sellModifier={this.sellModifier}
                      />
                    }
                    {(isOption) &&
                      <Options
                        selectedLine={selectedLine}
                        selectedParent={selectedParent}
                        sellOption={this.sellOption}
                      />
                    }
                  </div>
                </div>
                <div className={classes.tabs}>
                  {this.renderTabs()}
                </div>
                <div className={classes.modifierButtons}>
                  <ButtonGrid
                    styleCell={{ padding: '2vh 2%' }}
                    direction="row"
                    cols={4}
                    rows={1}
                    buttons={modifierButtons}
                  />
              </div>
              </div>
            }
            {!isSearch && (isCombo || !showModifierScreen || !inProgress) &&
              <div className={classes.absoluteWrapper}>
                <NavigationGrid
                  groups={this.groupsByTab[selectedTabIdx]}
                  sellFunc={this.sellItem}
                  cols={8}
                  rows={9}
                  expandCol={6}
                  groupsPerCol={1}
                  maxSpanCols={4}
                  filterClass={`${this.NAVIGATION_MENU}`}
                  styleTitle={(themeName === 'dark') ? this.styleTitleDark : this.styleTitle}
                  buttonProps={{ blockOnActionRunning: true }}
                />
              </div>
            }
            {isSearch &&
              <ProductSearch onSellItem={this.sellItem} />
            }
          </div>
        </div>
      </div>
    )
  }
}

SaleScreen.propTypes = {
  /**
   * Injected classes
   * @ignore
   */
  classes: PropTypes.object,
  /**
   * Order state from `orderReducer`
   */
  order: PropTypes.object,
  /**
   * Order time stamp from `orderLastTimestamp`
   */
  orderLastTimestamp: PropTypes.number,
  /**
   * Custom state from `customModelReducer`
   */
  custom: PropTypes.object,
  /**
   * Navigation state from `navigationReducer`
   */
  navigation: PropTypes.object,
  /**
   * Modifiers from `modifiersReducer`
   */
  modifiers: PropTypes.object,
  /**
   * Current theme name
   */
  themeName: PropTypes.string
}

SaleScreen.defaultProps = {
  order: {},
  navigation: {},
  modifiers: {},
  custom: {}
}

function mapStateToProps({ order, navigation, modifiers, custom, orderLastTimestamp }) {
  return {
    order,
    navigation,
    modifiers,
    custom,
    orderLastTimestamp,
    themeName: (custom || {}).THEME || 'default'
  }
}

export default connect(mapStateToProps)(injectSheet(styles)(SaleScreen))
