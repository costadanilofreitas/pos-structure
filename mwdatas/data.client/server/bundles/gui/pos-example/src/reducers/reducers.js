import { combineReducers } from 'redux'
import {
  posIdReducer, loadingReducer, localeReducer, navigationReducer, infoMessageReducer,
  customModelReducer, operatorReducer, posStateReducer, mwActionReducer, dialogsReducer,
  orderReducer
} from 'posui/reducers'

const rootReducer = combineReducers({
  posId: posIdReducer,
  loading: loadingReducer,
  locale: localeReducer,
  navigation: navigationReducer,
  custom: customModelReducer,
  infoMessage: infoMessageReducer,
  operator: operatorReducer,
  posState: posStateReducer,
  actionRunning: mwActionReducer,
  dialogs: dialogsReducer,
  order: orderReducer
})

export default rootReducer
