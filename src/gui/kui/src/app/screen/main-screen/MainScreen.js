import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { bindActionCreators } from 'redux'
import { FlexChild, FlexGrid } from '3s-widgets'
import { I18N } from '3s-posui/core'

import MessageBus from '../../../util/MessageBus'
import KdsHeader from '../../component/kds-header'
import ExpoBody from '../expo-screen/expo-body'
import KdsFooter from '../../component/kds-footer'
import prepColumns from '../../../constants/prepColumns'
import ConsolidatedItemsDialog from '../../component/dialogs/ConsolidatedItemsDialog'
import PrepLines from '../prep-screen/prep-lines'
import FullContainer from '../../styled-components/StyledComponents'
import { TabButton, TabContainer } from './StyledMainScreen'
import withState from '../../../util/withState'
import { setKdsViewAction, setZoomAction } from '../../../actions'
import PickBody from '../pick-screen/pick-body'
import { deepEquals } from '../../../util/renderUtil'

class MainScreen extends Component {
  constructor(props) {
    super(props)

    const kdsModel = this.props.kdsModel

    this.msgBus = new MessageBus(kdsModel.id)
    this.configuredBumpBar = kdsModel.bumpbar
    this.bumpBarName = kdsModel.bumpbar != null ? kdsModel.bumpbar.name : null

    this.handleKeyDown = this.handleKeyDown.bind(this)
    this.handleZoom = this.handleZoom.bind(this)
    this.handleRefreshScreen = this.handleRefreshScreen.bind(this)
    this.handleUndo = this.handleUndo.bind(this)
    this.handleViewChange = this.handleViewChange.bind(this)
    this.handleShowConsolidatedItems = this.handleShowConsolidatedItems.bind(this)

    this.lastKeyDown = new Date().getTime()
    if (this.configuredBumpBar != null) {
      this.bumpbarKeys = new Set(Object.values(this.configuredBumpBar).reduce((arr, cur) => {
        if (cur.commands) {
          Object.values(cur.commands).forEach(command => arr.push(...command))
        }
        return arr
      }, []))
    }
  }

  shouldComponentUpdate(nextProps) {
    const currentViews = this.props.kdsModel.views
    const currentSelectedView = currentViews == null ? null : currentViews.filter(x => x.selected)[0]

    const nextViews = nextProps.kdsModel.views
    const nextSelectedView = nextViews == null ? null : nextViews.filter(x => x.selected)[0]

    const currentKdsLayout = this.props.kdsModel.layout
    const nextKdsLayout = nextProps.kdsModel.layout

    if (this.kdsModelWasChanged(currentKdsLayout, nextKdsLayout, currentSelectedView, nextSelectedView)) {
      return true
    }

    if (this.props.consolidatedItems !== nextProps.consolidatedItems) {
      return true
    }

    const currentOrders = this.getOrders(currentSelectedView, this.props.viewsOrders).orders
    const nextOrders = this.getOrders(nextSelectedView, nextProps.viewsOrders).orders

    if (currentOrders.length !== nextOrders.length) {
      return true
    } else if (nextOrders.length !== 0) {
      return !deepEquals(nextOrders, currentOrders)
    }

    return false
  }

  render() {
    const { kdsModel, viewsOrders } = this.props
    const activeTab = kdsModel.displayMode.toLowerCase()
    const pickupDisplayMode = this.isPickupDisplayMode(activeTab)
    const selectedView = kdsModel.views == null ? null : kdsModel.views.filter(x => x.selected)[0]
    const ordersLines = this.getOrders(selectedView, viewsOrders)
    const orders = ordersLines.orders
    const lines = ordersLines.lines
    const viewWithActions = kdsModel.viewWithActions

    return (
      <FullContainer className={`display-${activeTab}`}>
        {this.showConsolidatedItems(orders)}
        <FlexGrid direction={'column'}>
          {kdsModel.views.length > 1 &&
          <FlexChild size={2}>
            {this.viewsChooser(kdsModel.views)}
          </FlexChild>}
          {this.renderHeader()}
          <FlexChild size={pickupDisplayMode ? 22 : 21.5}>
            {this.bodyChooser(activeTab, selectedView, orders, lines, viewWithActions)}
          </FlexChild>
          {this.renderFooter(selectedView, orders)}
        </FlexGrid>
      </FullContainer>
    )
  }

  componentDidMount() {
    document.addEventListener('keydown', this.handleKeyDown)
  }

  componentWillUnmount() {
    document.removeEventListener('keydown', this.handleKeyDown)
  }

  kdsModelWasChanged(currentKdsLayout, nextKdsLayout, currentSelectedView, nextSelectedView) {
    if (JSON.stringify(currentKdsLayout) !== JSON.stringify(nextKdsLayout)) {
      return true
    }

    if (currentSelectedView.name !== nextSelectedView.name) {
      return true
    }

    return false
  }

  handleViewChange(view) {
    const { setKdsView } = this.props
    setKdsView(view)
  }

  getOrders(selectedView, viewsOrders) {
    if (selectedView == null || viewsOrders == null) {
      return { orders: [], lines: [] }
    }

    const currentView = viewsOrders[selectedView.productionView]
    if (currentView == null) {
      return { orders: [], lines: [] }
    }

    const lines = currentView.lines
    return { orders: currentView.orders, lines: lines }
  }

  isPickupDisplayMode(activeTab) {
    return activeTab === 'pick'
  }

  showConsolidatedItems(orders) {
    const { consolidatedItems } = this.props
    if (!consolidatedItems) {
      return null
    }

    return (
      <ConsolidatedItemsDialog
        items={orders}
        handleClose={this.handleShowConsolidatedItems}
      />
    )
  }

  viewsChooser(views) {
    const handleViewChange = this.handleViewChange

    return (
      <TabContainer>
        {views.map(function (view, index) {
          return (
            <TabButton
              key={`tabButton_${index}`}
              onClick={() => handleViewChange(view.name)}
              selected={view.selected}
              className={`test_MainScreen_TAB-${index}`}
            >
              <I18N id={`$${view.title}`}/>
            </TabButton>
          )
        })}
      </TabContainer>
    )
  }

  renderHeader() {
    const { kdsModel } = this.props
    const activeTab = kdsModel.displayMode.toLowerCase()

    const header = this.headerChooser(activeTab)
    if (header != null) {
      return header
    }
    return null
  }

  headerChooser(activeTab) {
    const { statistics, views } = this.props.kdsModel
    if (activeTab === 'expo' || activeTab === 'prep') {
      return (
        <KdsHeader statistics={statistics} views={views}/>
      )
    }
    return null
  }

  bodyChooser(activeTab, selectedView, orders, lines, viewWithActions) {
    const { kdsModel } = this.props

    if (activeTab === 'expo') {
      return <ExpoBody orders={orders}/>
    } else if (activeTab === 'prep') {
      let columns = prepColumns
      if (!viewWithActions) {
        columns = columns.filter(function (column) {
          return column.renderer !== 'LineActionsRenderer'
        })
      }

      return <PrepLines columns={columns} lines={lines} kdsModel={kdsModel}/>
    } else if (activeTab === 'pick') {
      return <PickBody orders={orders}/>
    }

    return null
  }

  renderFooter(selectedView, orders) {
    const { kdsModel } = this.props
    const activeTab = kdsModel.displayMode.toLowerCase()

    const footer = this.footerChooser(activeTab, kdsModel.views, selectedView, orders)
    if (footer != null) {
      return (
        <FlexChild>
          {footer}
        </FlexChild>
      )
    }
    return null
  }

  footerChooser(activeTab, views, selectedView, orders) {
    const ordersQuantity = this.getOrdersQuantity(activeTab, orders)
    if (activeTab === 'expo' || activeTab === 'prep') {
      const isPrep = activeTab === 'prep'
      return (
        <KdsFooter
          handleZoom={this.handleZoom}
          handleRefreshScreen={this.handleRefreshScreen}
          handleShowConsolidatedItems={this.handleShowConsolidatedItems}
          handleUndo={this.handleUndo}
          showPageNavigation={!isPrep}
          showPagination={!isPrep}
          ordersQuantity={ordersQuantity}
          ordersTotal={orders.length}
          selectedView={selectedView}
        />
      )
    }

    return null
  }

  getOrdersQuantity(activeTab, orders) {
    if (activeTab === 'prep') {
      return orders.reduce((a, b) => a + (b.items.length || 0), 0)
    }

    const ordersArray = orders.map(a => a.attrs.order_id)
    return ordersArray.filter(this.onlyUnique).length
  }

  onlyUnique(value, index, self) {
    return self.indexOf(value) === index
  }

  handleKeyDown(evt) {
    const now = new Date().getTime()
    if (now > this.lastKeyDown + 130) {
      const code = evt.which || evt.keyCode
      if (code && this.bumpBarName) {
        this.msgBus.sendKDSBumpBarEvent(this.bumpBarName, code)
        if (this.bumpbarKeys.has(evt.keyCode)) {
          evt.preventDefault()
        }
      }
      this.lastKeyDown = now
    }
  }

  sendKDSBumpBarEvent(command) {
    const bumpExpo = this.configuredBumpBar
    const code = bumpExpo && bumpExpo.commands && bumpExpo.commands[command] && bumpExpo.commands[command][0]
    if (code) {
      this.msgBus.sendKDSBumpBarEvent(this.bumpBarName, code)
    }
  }

  handleZoom(view) {
    const { setZoom } = this.props
    setZoom(view.productionView)
  }

  handleRefreshScreen() {
    this.sendKDSBumpBarEvent('refreshscreen')
  }

  handleShowConsolidatedItems() {
    this.sendKDSBumpBarEvent('consolidateditems')
  }

  handleUndo(selectedView) {
    this.msgBus.sendKDSUndoServe(selectedView.productionView)
  }
}

MainScreen.propTypes = {
  consolidatedItems: PropTypes.bool,
  kdsModel: PropTypes.object,
  theme: PropTypes.object,
  viewsOrders: PropTypes.object,
  setKdsView: PropTypes.func,
  setZoom: PropTypes.func
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators(
    {
      setKdsView: setKdsViewAction,
      setZoom: setZoomAction
    }, dispatch)
}

export default withState(MainScreen, mapDispatchToProps)
