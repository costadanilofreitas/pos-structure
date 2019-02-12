import { createStore, applyMiddleware, compose } from 'redux'
import createSagaMiddleware from 'redux-saga'
import { eventLoopMiddleware, globalTimerMiddleware, i18nSaga, executeSaga } from 'posui/core'
import rootReducer from '../reducers/reducers'
import { loadProductDataSaga } from '../sagas'

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
  sagaMiddleware.run(globalTimerMiddleware)
  sagaMiddleware.run(i18nSaga)
  sagaMiddleware.run(executeSaga, posId)
  sagaMiddleware.run(loadProductDataSaga, posId)

  return store
}

export default configureStore
