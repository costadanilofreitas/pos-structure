import { combineReducers } from 'redux'
import PropTypes from 'prop-types'

import userReducer from './userReducer'
import productListReducer from './productListReducer'
import modifiersReducer from './modifiersReducer'
import genericReducer from './genericReducer'
import productCategoriesReducer from './productCategoriesReducer'

const rootReducer = combineReducers({
  user: userReducer,
  productList: productListReducer,
  modifiersList: modifiersReducer,
  generic: genericReducer,
  productCategories: productCategoriesReducer
})

export default rootReducer

/**
 * @typedef {object} user
 * @property {string} username
 * @property {string} token
 */

export const UserPropTypes = PropTypes.shape({
  username: PropTypes.string,
  token: PropTypes.string
})
/**
 * @typedef {Product[]} products
 */

/**
 * @typedef {object} Product
 * @property {number} partCode
 * @property {string} productName
 * @property {number} price
 * @property {bool} canChangePrice
 */
