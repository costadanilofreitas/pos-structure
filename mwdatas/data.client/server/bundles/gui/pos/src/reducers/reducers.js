import { combineReducers } from 'redux'
import {
  posIdReducer, loadingReducer, localeReducer, navigationReducer, infoMessageReducer,
  customModelReducer, operatorReducer, posStateReducer, mwActionReducer, dialogsReducer,
  orderReducer, modifiersReducer, orderLastTimestampReducer, drawerStateReducer,
  globalTimerReducer, timeDeltaReducer, themeReducer, workingModeReducer
} from 'posui/reducers'
import menuReducer from './menuReducer'
import currentMenuReducer from './currentMenuReducer'
import productDataReducer from './productDataReducer'

const rootReducer = combineReducers({
  posId: posIdReducer,
  loading: loadingReducer,
  locale: localeReducer,
  navigation: navigationReducer,
  custom: customModelReducer,
  infoMessage: infoMessageReducer,
  operator: operatorReducer,
  posState: posStateReducer,
  drawerState: drawerStateReducer,
  actionRunning: mwActionReducer,
  dialogs: dialogsReducer,
  order: orderReducer,
  orderLastTimestamp: orderLastTimestampReducer,
  menu: menuReducer,
  modifiers: modifiersReducer,
  currentMenu: currentMenuReducer,
  globalTimer: globalTimerReducer,
  timeDelta: timeDeltaReducer,
  theme: themeReducer,
  products: productDataReducer,
  workingMode: workingModeReducer
})

export default rootReducer
