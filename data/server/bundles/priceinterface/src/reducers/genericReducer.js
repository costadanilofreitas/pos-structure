import {
  GET_ALL_DATA_ERROR,
  GET_ALL_DATA_SUCCESS,
  LOADING_ALL_DATA,
  RESET_ALL_DATA,
  RESET_PRODUCT,
  SAVE_PRODUCT_ERROR,
  SAVE_PRODUCT_SUCCESS
} from '../common/constants'
import { CANCELING_EDITING_ITEM, CHANGE_PRICE_ITEM, EDITING_ITEM } from '../actions/genericListActions'

function createNewState(state, product, changeProductFunc) {
  const newData = []
  let priceChanged = {}
  for (let i = 0; i < state.data.length; i++) {
    newData.push(Object.assign({}, state.data[i]))
    if (state.data[i].partCode === product.partCode) {
      newData[i] = changeProductFunc(state.data[i])
      priceChanged = {
        line: Object.assign({}, newData[i]),
        price: newData[i].price
      }
    }
  }
  return { data: newData, priceChanged: priceChanged }
}

function updateItemsState(state, partCode, comboPartCode, editing, price) {
  const newData = []
  let newPrice = 0
  let originalPrice = 0

  for (let i = 0; i < state.data.length; i++) {
    newData.push(Object.assign({}, state.data[i]))

    if (newData[i].comboPartCode === undefined) {
      if (newData[i].partCode === partCode) {
        originalPrice = newData[i].price

        newData[i].editing = editing !== undefined ? editing : newData[i].editing
        newData[i].price = price !== undefined ? price : newData[i].price

        newPrice = newData[i].price
      } else {
        newData[i].editing = false
      }
    } else if (state.data[i].comboPartCode === comboPartCode) {
      originalPrice = newData[i].price

      newData[i].editing = editing !== undefined ? editing : newData[i].editing
      newData[i].price = price !== undefined ? price : newData[i].price

      newPrice = newData[i].price
    } else {
      newData[i].editing = false
    }
  }
  return { data: newData, newPrice: newPrice, originalPrice: originalPrice }
}

const genericReducer = (state = {}, action) => {
  switch (action.type) {
  case RESET_ALL_DATA:
    return { data: [], priceChanged: null, loadingData: false }
  case LOADING_ALL_DATA:
    return { data: [], priceChanged: null, loadingData: true }
  case GET_ALL_DATA_SUCCESS:
    return { data: action.data, priceChanged: null, loadingData: false }
  case GET_ALL_DATA_ERROR:
    return { data: action.error, priceChanged: null, loadingData: false }
  case SAVE_PRODUCT_SUCCESS:
    return (
      createNewState(
        state,
        action.priceChanged.line,
        () => {
          return Object.assign(
            {},
            action.priceChanged.line,
            { price: action.priceChanged.price,
              saving: false,
              saveError: false,
              saved: true,
              priceChanged: true
            }
          )
        }
      )
    )
  case SAVE_PRODUCT_ERROR:
    return (
      createNewState(
        state,
        action.response,
        () => {
          return Object.assign(
            {},
            action.response.status,
            action.response,
            {
              price: action.response.price,
              saving: false,
              saveError: action.response.saveError,
              saved: false,
              partCode: action.response.partCode,
              comboPartCode: action.response.comboPartCode,
              productName: action.response.productName
            }
          )
        }
      )
    )
  case RESET_PRODUCT:
    return (
      createNewState(
        state,
        action.priceChanged.line,
        () => {
          return Object.assign(
            {},
            action.priceChanged.line,
            { saving: false, saveError: false, saved: false }
          )
        }
      )
    )
  case EDITING_ITEM:
    return (
      updateItemsState(
        state,
        action.partCode,
        action.comboPartCode,
        true
      )
    )
  case CANCELING_EDITING_ITEM:
    return (
      updateItemsState(
        state,
        action.partCode,
        action.comboPartCode,
        false
      )
    )
  case CHANGE_PRICE_ITEM:
    return (
      updateItemsState(
        state,
        action.partCode,
        action.comboPartCode,
        action.editing,
        action.price
      )
    )
  default:
    return state
  }
}

export default genericReducer
