import { createStore, applyMiddleware, compose } from 'redux'
import ReduxPromise from 'redux-promise';
import thunk from 'redux-thunk'
import rootReducer from '../reducers/reducers'

const configureStore = preloadedState => {
  const store = createStore(
    rootReducer,
    preloadedState,
    applyMiddleware(thunk, ReduxPromise),
  )
  
  return store
}

export default configureStore
