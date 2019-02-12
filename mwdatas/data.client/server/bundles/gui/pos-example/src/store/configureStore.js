import { createStore, applyMiddleware, compose } from 'redux'
import createSagaMiddleware from 'redux-saga'
import { eventLoopMiddleware, i18nSaga, executeSaga } from 'posui/core'
import rootReducer from '../reducers/reducers'

const sagaMiddleware = createSagaMiddleware()

const configureStore = preloadedState => {
  let composeEnhancers
  if (process.env.NODE_ENV === 'production') {
    composeEnhancers = compose
  } else {
    /* eslint-disable no-underscore-dangle */
    composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose
    /* eslint-enable */
  }
  const store = createStore(
    rootReducer,
    preloadedState,
    composeEnhancers(applyMiddleware(sagaMiddleware))
  )

  const posId = store.getState().posId
  sagaMiddleware.run(eventLoopMiddleware, posId)
  sagaMiddleware.run(i18nSaga)
  sagaMiddleware.run(executeSaga, posId)

  return store
}

export default configureStore
