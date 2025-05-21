import { combineReducers } from 'redux'

import saleTypeReducer from '../ducks/saleType'

const rootDucksReducer = combineReducers({
  saleType: saleTypeReducer
})

export default rootDucksReducer
