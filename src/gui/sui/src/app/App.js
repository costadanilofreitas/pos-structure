import React, { Component } from 'react'
import { bindActionCreators } from 'redux'
import PropTypes from 'prop-types'
import _, { debounce } from 'lodash'
import { Helmet } from 'react-helmet'
import { ThemeProvider as ReactThemeProvider } from 'react-jss'
import { ThemeProvider as StyleThemeProvider } from 'styled-components'

import { LoadingScreen, ScreenSize } from '3s-posui/widgets'
import { setThemeAction } from '3s-posui/actions'

import DialogList from '../component/dialogs/DialogList'
import themes from '../constants/themes'
import MainScreen from './screen/main-screen'
import BlockDialog from '../component/dialogs/block-dialog'
import withState from '../util/withState'


import loadSelectTableAction from '../actions/loadSelectTableAction'
import staticConfigModified from '../actions/staticConfigModified'
import loadSpecialCatalogAction from '../actions/loadSpecialCatalogAction'
import loadProductDataAction from '../actions/loadProductDataAction'
import loadTefAvailableAction from '../actions/loadTefAvailableAction'
import loadStoredOrdersAction from '../actions/loadStoredOrdersAction'
import loadFloorPlanAction from '../actions/loadFloorPlanAction'
import loadUserListAction from '../actions/loadUserListAction'
import loadPosModelAction from '../actions/loadPosModelAction'
import loadThemeConfigurationAction from '../actions/loadThemeConfigurationAction'
import updateWindowSize from '../actions/updateWindowSize'
import InfoMessageDialog from '../component/dialogs/eft-dialog'
import AutoLogout from './component/auto-logout'
import StaticConfigPropTypes from '../prop-types/StaticConfigPropTypes'
import DeviceType from '../constants/Devices'
import loadNavigationDataAction from '../actions/loadNavigationDataAction'
import loadModifiersDataAction from '../actions/loadModifiersDataAction'


class App extends Component {
  constructor(props) {
    super(props)

    props.loadSelectedTable()
    props.loadSpecialCatalog()
    props.loadStaticConfig()
    props.loadTefAvailable()
    props.loadProductData()
    props.loadStoredOrdersAction()
    props.loadFloorPlanAction()
    props.loadUserListAction()
    props.loadThemeConfigurationAction()
    props.loadNavigationData()
    props.loadModifiersData()
    props.loadPosModelAction()

    this.setCurrentTheme(props)
    this.isLoading = this.isLoading.bind(this)
  }

  render() {
    const TITLE = `E-DEPLOY POS SUI [${this.props.posId}]`
    return (
      <ReactThemeProvider theme={this.props.theme}>
        <StyleThemeProvider theme={this.props.theme}>
          <LoadingScreen customLoadingFlag={this.isLoading()} style={{ height: '100%' }}>
            <Helmet>
              <title> {TITLE} </title>
            </Helmet>
            <DialogList flatStyle={this.props.deviceType !== DeviceType.Totem}/>
            <BlockDialog/>
            <MainScreen/>
            <ScreenSize/>
            <AutoLogout/>
            <InfoMessageDialog flatStyle={this.props.deviceType !== DeviceType.Totem}/>
          </LoadingScreen>
        </StyleThemeProvider>
      </ReactThemeProvider>
    )
  }

  componentDidMount() {
    this.props.updateWindowSize(window.innerWidth, window.innerHeight)

    const ref = this
    window.addEventListener('resize', debounce(function () {
      ref.props.updateWindowSize(window.innerWidth, window.innerHeight)
    }, 200))
  }

  componentDidCatch = (error, errorInfo) => {
    console.error(`APP JS ERROR: ${error.toString()}`)
    console.error(`APP JS ERROR_INFO: ${errorInfo.componentStack}`)
    setTimeout(() => window.location.reload(true), 5000)
  }

  setCurrentTheme = (props) => {
    const theme = _.get(props, 'custom.THEME', 'DEFAULT')
    props.setThemeAction(_.find(themes, ['name', theme]))
  }

  componentDidUpdate(prevProps) {
    if (_.get(prevProps, 'custom.THEME', 'default') !== _.get(this.props, 'custom.THEME', 'default')) {
      this.setCurrentTheme(this.props)
    }
  }

  isLoading() {
    const stillLoading =
      this.props.locale == null ||
      this.props.floorPlan == null ||
      this.props.staticConfig == null ||
      this.props.products == null ||
      this.props.navigation == null ||
      this.props.tableLists == null ||
      this.props.modifiers == null

    return stillLoading
  }
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators(
    {
      loadSelectedTable: loadSelectTableAction,
      loadSpecialCatalog: loadSpecialCatalogAction,
      loadStaticConfig: staticConfigModified,
      loadTefAvailable: loadTefAvailableAction,
      loadProductData: loadProductDataAction,
      loadStoredOrdersAction: loadStoredOrdersAction,
      loadFloorPlanAction: loadFloorPlanAction,
      loadUserListAction: loadUserListAction,
      loadThemeConfigurationAction: loadThemeConfigurationAction,
      loadNavigationData: loadNavigationDataAction,
      loadModifiersData: loadModifiersDataAction,
      loadPosModelAction: loadPosModelAction,
      updateWindowSize,
      setThemeAction
    }, dispatch)
}

App.propTypes = {
  posId: PropTypes.number,
  deviceType: PropTypes.number,
  theme: PropTypes.object,
  locale: PropTypes.object,
  floorPlan: PropTypes.object,
  staticConfig: StaticConfigPropTypes,
  products: PropTypes.object,
  tableLists: PropTypes.object,
  navigation: PropTypes.array,
  modifiers: PropTypes.object,
  loadProductData: PropTypes.func,
  loadSelectedTable: PropTypes.func,
  loadSpecialCatalog: PropTypes.func,
  loadStaticConfig: PropTypes.func,
  loadTefAvailable: PropTypes.func,
  loadStoredOrdersAction: PropTypes.func,
  loadFloorPlanAction: PropTypes.func,
  loadUserListAction: PropTypes.func,
  loadThemeConfigurationAction: PropTypes.func,
  loadNavigationData: PropTypes.func,
  loadModifiersData: PropTypes.func,
  loadPosModelAction: PropTypes.func,
  updateWindowSize: PropTypes.func
}

App.defaultProps = {
  theme: {}
}

export default withState(
  App, mapDispatchToProps, 'posId', 'deviceType', 'locale', 'floorPlan', 'staticConfig', 'products', 'navigation',
  'tableLists', 'theme', 'screenOrientation', 'modifiers'
)
