import { createStore, applyMiddleware, compose } from 'redux'
import createSagaMiddleware from 'redux-saga'
import thunk from 'redux-thunk'

import rootReducer from '../reducers/reducers'
import { root } from '../saga/sagas'

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
    composeEnhancers(applyMiddleware(thunk, sagaMiddleware))
  )

  store.runSaga = sagaMiddleware.run(root)
  return store
}

export default configureStore
