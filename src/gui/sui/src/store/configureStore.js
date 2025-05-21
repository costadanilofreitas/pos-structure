import { createStore, applyMiddleware, compose } from 'redux'
import createSagaMiddleware from 'redux-saga'
import { i18nSaga, executeSaga } from '3s-posui/core'
import eventLoopMiddleware from './eventLoopMiddleware'

import rootReducer from '../reducers'
import loadStaticConfig from '../saga/loadStaticConfigSaga'
import loadSpecialCatalog from '../saga/loadSpecialCatalogSaga'
import loadSelectedTable from '../saga/loadSelectedTableSaga'
import loadProductDataSaga from '../saga/loadProductDataSaga'
import loadNavigationDataSaga from '../saga/loadNavigationDataSaga'
import loadTefAvailableSaga from '../saga/loadTefAvailableSaga'
import abandonPos from '../saga/abandonPos'
import loadFloorPlanSaga from '../saga/loadFloorPlanSaga'
import loadUserListSaga from '../saga/loadUserListSaga'
import loadModifiersDataSaga from '../saga/loadModifiersDataSaga'
import loadMobilePrintSaga from '../saga/loadMobilePrintSaga'
import loadMobileConfirmTransactionSaga from '../saga/loadMobileConfirmTransactionSaga'
import loadScannerDataSaga from '../saga/loadScannerDataSaga'
import { loadStoredOrdersSaga, reloadStoredOrdersSaga } from '../saga/loadStoredOrdersSaga'
import { loadSatStatusSaga, reloadSatStatusSaga } from '../saga/loadSatStatusSaga'
import { loadRemoteOrderStatusSaga, reloadRemoteOrderStatusSaga } from '../saga/loadRemoteOrderStatusSaga'
import customEventSaga from '../saga/customEventSaga'
import loadPosModelSaga from '../saga/loadPosModelSaga'
import loadThemeConfigurationsSaga from '../saga/loadThemeConfigurationSaga'

const sagaMiddleware = createSagaMiddleware()

const configureStore = preloadedState => {
  let composeEnhancers
  /* eslint-disable no-underscore-dangle */
  if (process.env.NODE_ENV === 'production') {
    composeEnhancers = compose
  } else if (window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__) {
    composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__({
      actionsBlacklist: ['GLOBAL_TIMER_TICK']
    }) || compose
  } else {
    composeEnhancers = compose
  }
  /* eslint-enable */
  const store = createStore(
    rootReducer,
    preloadedState,
    composeEnhancers(applyMiddleware(sagaMiddleware))
  )

  const posId = store.getState().posId
  sagaMiddleware.run(eventLoopMiddleware, posId, 'POS', true)
  sagaMiddleware.run(i18nSaga)
  sagaMiddleware.run(executeSaga, posId)
  sagaMiddleware.run(loadStaticConfig, posId)
  sagaMiddleware.run(loadSpecialCatalog, posId)
  sagaMiddleware.run(loadSelectedTable, posId)
  sagaMiddleware.run(loadProductDataSaga, posId)
  sagaMiddleware.run(loadNavigationDataSaga, posId)
  sagaMiddleware.run(loadModifiersDataSaga, posId)
  sagaMiddleware.run(loadTefAvailableSaga, posId)
  sagaMiddleware.run(abandonPos, posId)
  sagaMiddleware.run(loadStoredOrdersSaga, posId)
  sagaMiddleware.run(reloadStoredOrdersSaga)
  sagaMiddleware.run(loadFloorPlanSaga, posId)
  sagaMiddleware.run(loadSatStatusSaga, posId)
  sagaMiddleware.run(loadMobilePrintSaga)
  sagaMiddleware.run(loadMobileConfirmTransactionSaga)
  sagaMiddleware.run(loadScannerDataSaga)
  sagaMiddleware.run(loadUserListSaga, posId)
  sagaMiddleware.run(reloadSatStatusSaga, posId)
  sagaMiddleware.run(customEventSaga, posId)
  sagaMiddleware.run(loadPosModelSaga, posId)
  sagaMiddleware.run(loadRemoteOrderStatusSaga, posId)
  sagaMiddleware.run(reloadRemoteOrderStatusSaga, posId)
  sagaMiddleware.run(loadThemeConfigurationsSaga)

  return store
}

export default configureStore

