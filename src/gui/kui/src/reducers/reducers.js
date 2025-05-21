import { combineReducers } from 'redux'
import {
  kdsIdReducer, loadingReducer, localeReducer, globalTimerReducer, themeReducer, timeDeltaReducer
} from '3s-posui/reducers'
import doneLinesReducer from './doneLinesReducer'
import heldLinesReducer from './heldLinesReducer'
import displayModeReducer from './displayModeReducer'
import currentLineReducer from './currentLineReducer'
import currentOrderReducer from './currentOrderReducer'
import consolidatedItemsReducer from './consolidatedItemsReducer'
import paginationBlockSizeReducer from './paginationBlockSizeReducer'
import currentOrderPageReducer from './currentOrderPageReducer'
import modelReducer from './modelReducer'
import viewsOrdersReducer from './viewsOrdersReducer'
import refreshEndReducer from './refreshEndReducer'

const rootReducer = combineReducers({
  consolidatedItems: consolidatedItemsReducer,
  currentLine: currentLineReducer,
  currentOrder: currentOrderReducer,
  currentOrderPage: currentOrderPageReducer,
  displayMode: displayModeReducer,
  doneLines: doneLinesReducer,
  globalTimer: globalTimerReducer,
  heldLines: heldLinesReducer,
  loading: loadingReducer,
  locale: localeReducer,
  kdsId: kdsIdReducer,
  kdsModel: modelReducer,
  paginationBlockSize: paginationBlockSizeReducer,
  timeDelta: timeDeltaReducer,
  theme: themeReducer,
  viewsOrders: viewsOrdersReducer,
  refreshEnd: refreshEndReducer
})

export default rootReducer
