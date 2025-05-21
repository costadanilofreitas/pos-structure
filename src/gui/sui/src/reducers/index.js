import { combineReducers } from 'redux'
import {
  buildsReducer,
  customModelReducer,
  dialogsReducer,
  drawerStateReducer,
  globalTimerReducer,
  infoMessageReducer,
  loadingReducer,
  localeReducer,
  mwActionReducer,
  orderLastTimestampReducer,
  posIdReducer,
  themeReducer,
  timeDeltaReducer,
  workingModeReducer
} from '3s-posui/reducers'

import menuReducer from './menuReducer'
import saleTypeReducer from '../ducks/saleType'
import mobileReducer from './mobileReducer'
import deviceReducer from './deviceReducer'
import selectedTableReducer from './selectedTableReducer'
import tableListsReducer from './tableListsReducer'
import floorPlanReducer from './floorPlanReducer'
import specialCatalogReducer from './specialCatalogReducer'
import tableInfoReducer from './tableInfoReducer'
import showTabsReducer from './showTabsReducer'
import productDataReducer from './productDataReducer'
import staticConfigReducer from './staticConfigReducer'
import tefAvailableReducer from './tefAvailableReducer'
import navigationReducer from './navigationReducer'
import orderFunTasticReducer from './orderFunTasticReducer'
import storedOrdersReducer from './storedOrdersReducer'
import satInfoReducer from './satInfoReducer'
import remoteOrderStatusReducer from './remoteOrderStatusReducer'
import posStateReducer from './posStateReducer'
import userListReducer from './userListReducer'
import screenOrientationReducer from './screenOrientationReducer'
import operatorReducer from './operatorReducer'
import modifiersReducer from './modifiersReducer'


const rootReducer = combineReducers({
  actionRunning: mwActionReducer,
  builds: buildsReducer,
  custom: customModelReducer,
  deviceType: deviceReducer,
  dialogs: dialogsReducer,
  drawerState: drawerStateReducer,
  floorPlan: floorPlanReducer,
  globalTimer: globalTimerReducer,
  infoMessage: infoMessageReducer,
  loading: loadingReducer,
  locale: localeReducer,
  mobile: mobileReducer,
  modifiers: modifiersReducer,
  navigation: navigationReducer,
  operator: operatorReducer,
  order: orderFunTasticReducer, // orderReducer,
  orderLastTimestamp: orderLastTimestampReducer,
  posId: posIdReducer,
  posState: posStateReducer,
  products: productDataReducer,
  saleType: saleTypeReducer,
  selectedMenu: menuReducer,
  selectedTable: selectedTableReducer,
  showTableInfo: tableInfoReducer,
  showTabs: showTabsReducer,
  specialCatalog: specialCatalogReducer,
  staticConfig: staticConfigReducer,
  storedOrders: storedOrdersReducer,
  tableLists: tableListsReducer,
  tefAvailable: tefAvailableReducer,
  satInfo: satInfoReducer,
  remoteOrderStatus: remoteOrderStatusReducer,
  screenOrientation: screenOrientationReducer,
  theme: themeReducer,
  timeDelta: timeDeltaReducer,
  userList: userListReducer,
  workingMode: workingModeReducer
})

export default rootReducer
