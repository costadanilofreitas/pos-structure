import { call, put, takeLatest, fork, all } from 'redux-saga/effects'

import {
  GET_ALL_DATA_REQUEST,
  GET_ALL_DATA_SUCCESS,
  GET_ALL_DATA_ERROR,
  SAVE_PRODUCT_REQUEST,
  SAVE_PRODUCT_SUCCESS,
  SAVE_PRODUCT_ERROR,
  RESET_EDITING_PRODUCT,
  RESET_PRODUCT,
  GET_MODIFIERS_REQUEST,
  GET_MODIFIERS_ERROR,
  MODIFIERS,
  GET_MODIFIERS_SUCCESS,
  SAVE_MODIFIER_REQUEST,
  RESET_ALL_DATA,
  LOADING_ALL_DATA
} from '../common/constants'

import { getAllData, saveModifier, saveProduct } from '../api/getData'

export function * getAllDataSaga(...args) {
  try {
    yield put({ type: RESET_ALL_DATA })
    yield put({ type: LOADING_ALL_DATA })
    const responseData = yield call(
      () => getAllData(args[0].dataRequest, args[0].token, args[0].productCategory)
    )

    // dispatch a success action to the store with the new object
    yield put({
      type: GET_ALL_DATA_SUCCESS,
      data: responseData.data
    })
  } catch (error) {
    yield put({
      type: GET_ALL_DATA_ERROR,
      error: error
    })
  }
}

export function * getAllModifiersSaga(...args) {
  try {
    yield put({ type: RESET_ALL_DATA })
    yield put({ type: LOADING_ALL_DATA })
    const responseData = yield call(() => getAllData(MODIFIERS, args[0].token))

    // dispatch a success action to the store with the object
    yield put({
      type: GET_MODIFIERS_SUCCESS,
      data: responseData.data
    })
  } catch (error) {
    yield put({
      type: GET_MODIFIERS_ERROR,
      error: error
    })
  }
}


export function * saveProductSaga(...args) {
  try {
    yield call(() => saveProduct(args[0].dataRequest,
                                 args[0].product,
                                 args[0].newPrice,
                                 args[0].token))

    yield put({
      type: SAVE_PRODUCT_SUCCESS,
      priceChanged: { line: args[0].product, price: args[0].newPrice } }
    )
  } catch (error) {
    const response = Object.assign({}, args[0].product, { saveError: error, saving: false })
    yield put({
      type: SAVE_PRODUCT_ERROR,
      response
    })
  }
}

export function * saveModifierSaga(...args) {
  try {
    yield call(() => saveModifier(args[0].product,
                                  args[0].newPrice,
                                  args[0].token,
                                  args[0].classCode))

    yield put({
      type: SAVE_PRODUCT_SUCCESS,
      priceChanged: { line: args[0].product, price: args[0].newPrice } }
    )
  } catch (error) {
    const response = Object.assign({}, args[0].product, { saveError: error, saving: false })
    yield put({
      type: SAVE_PRODUCT_ERROR,
      response
    })
  }
}

export function * resetProductSaga(...args) {
  const response = Object.assign({}, args[0].product, { saveError: null, saving: false })
  yield put({
    type: RESET_PRODUCT,
    response: response,
    priceChanged: null
  })
}


export function * workerGetAllData() {
  yield takeLatest(GET_ALL_DATA_REQUEST, getAllDataSaga)
}

export function * workerSaveProduct() {
  yield takeLatest(SAVE_PRODUCT_REQUEST, saveProductSaga)
}

export function * workerSaveModifier() {
  yield takeLatest(SAVE_MODIFIER_REQUEST, saveModifierSaga)
}

export function * workerCancelProduct() {
  yield takeLatest(RESET_EDITING_PRODUCT, resetProductSaga)
}

export function * workerGetAllModifiers() {
  yield takeLatest(GET_MODIFIERS_REQUEST, getAllModifiersSaga)
}

// watcher saga: watches for actions dispatched to the store, starts worker saga
export function * root() {
  yield all([
    fork(workerGetAllData),
    fork(workerGetAllModifiers),
    fork(workerSaveProduct),
    fork(workerSaveModifier),
    fork(workerCancelProduct)
  ])
}

