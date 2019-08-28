import PropTypes from 'prop-types'

import {
  CANCEL_EDITING_PRODUCT,
  ERROR_SAVING_PRODUCT,
  GET_PRODUCTS,
  GET_PRODUCTS_ERROR,
  PRODUCT_SAVED,
  SAVING_PRODUCT,
  START_EDITING_PRODUCT
} from '../common/constants'

function createNewState(state, product, changeProductFunc) {
  const newState = []
  for (let i = 0; i < state.products.length; i++) {
    newState.push(Object.assign({}, state.products[i]))
    if (state.products[i].partCode === product.partCode) {
      newState[i] = changeProductFunc(state.products[i])
    }
  }
  return { products: newState, loadingError: null }
}

export default function productsReducer(state = null, action) {
  switch (action.type) {
  case GET_PRODUCTS:
    return action.productList
  case GET_PRODUCTS_ERROR:
    return action.productList
  case PRODUCT_SAVED: {
    return createNewState(state,
                          action.product,
                          product => {
                            return Object.assign(
                              {},
                              product,
                              {
                                price: action.product.price,
                                editing: false,
                                saving: false
                              }
                           )
                          }
    )
  }
  case SAVING_PRODUCT: {
    return createNewState(state,
                          action.product,
                          product => {
                            return Object.assign(
                              {},
                              product,
                              {
                                price: action.product.price,
                                editing: false,
                                saving: true
                              }
                            )
                          }
    )
  }

  case ERROR_SAVING_PRODUCT: {
    return createNewState(state,
                          action.product,
                          product => {
                            return Object.assign(
                              {},
                              product,
                              {
                                price: action.product.price,
                                editing: true,
                                saving: false,
                                errorSaving: action.product.errorSaving
                              }
                            )
                          }
    )
  }
  case START_EDITING_PRODUCT: {
    return createNewState(state,
                          action.product,
                          product => {
                            return Object.assign(
                              {},
                              product,
                              {
                                price: action.product.price,
                                editing: true,
                                saving: false,
                                errorSaving: null
                              }
                            )
                          }
    )
  }
  case CANCEL_EDITING_PRODUCT: {
    return createNewState(state,
                          action.product,
                          product => {
                            return Object.assign(
                              {},
                              product,
                              {
                                price: action.product.price,
                                saving: false,
                                saveError: null
                              }
                            )
                          }
    )
  }
  default:
    return state
  }
}

export const DataPropTypes = PropTypes.shape({
  canChangePrice: PropTypes.bool,
  partCode: PropTypes.number,
  comboPartCode: PropTypes.number,
  optionPartCode: PropTypes.number,
  productName: PropTypes.string,
  price: PropTypes.number,
  product_price: PropTypes.number,
  saving: PropTypes.bool,
  errorSaving: PropTypes.object
})

export const PriceChangedPropTypes = PropTypes.shape({
  line: PropTypes.object,
  price: PropTypes.object
})

export const GenericDataPropTypes = PropTypes.shape({
  data: PropTypes.arrayOf(DataPropTypes),
  priceChanged: PriceChangedPropTypes,
  fetching: PropTypes.object,
  error: PropTypes.object,
  onRequestData: PropTypes.object
})
