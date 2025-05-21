/* eslint-disable no-underscore-dangle */
import { createStore, applyMiddleware, compose } from 'redux'
import createSagaMiddleware from 'redux-saga'
import { globalTimerMiddleware, i18nSaga } from '3s-posui/core'
import { eventLoopMiddleware } from './'

import kdsSaga from '../app/saga/kdsSaga'
import rootReducer from '../reducers/reducers'
import loadKdsModelSaga from '../saga/loadKdsModelSaga'
import setKdsViewSaga from '../saga/setKdsViewSaga'
import setKdsZoomSaga from '../saga/setKdsZoomSaga'
import loadThemeConfigurationsSaga from '../saga/loadThemeConfigurationSaga'

const sagaMiddleware = createSagaMiddleware()

const configureStore = preloadedState => {
  let composeEnhancers
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

  const kdsId = store.getState().kdsId
  sagaMiddleware.run(eventLoopMiddleware, kdsId, 'KDS')
  sagaMiddleware.run(globalTimerMiddleware)
  sagaMiddleware.run(kdsSaga, kdsId)
  sagaMiddleware.run(i18nSaga)
  sagaMiddleware.run(loadKdsModelSaga, kdsId)
  sagaMiddleware.run(setKdsViewSaga, kdsId)
  sagaMiddleware.run(setKdsZoomSaga, kdsId)
  sagaMiddleware.run(loadThemeConfigurationsSaga)

  return store
}

export default configureStore
