import { takeEvery } from 'redux-saga/effects'
import { MOBILE_CONFIRM_TRANSACTION } from '../constants/actionTypes'


function handleProcessPayment(status, message, payload) {
  if (status !== '0') {
    console.error(`${message} - ${payload}`)
  }
}

function fetchMobileConfirmTransaction(action) {
  if (window.mwapi != null && window.processPaymentCallback == null) {
    window.processPaymentCallback = handleProcessPayment
  }

  if (window.mwapi != null) {
    window.mwapi.processPayment('processPaymentCallback', '', '', action.payload['#text'], '1')
  } else {
    console.error('Device not initialized')
  }
}

function* loadMobileConfirmTransactionSaga() {
  if (window.mwapi != null) {
    window.processPaymentCallback = handleProcessPayment
  }

  yield takeEvery([MOBILE_CONFIRM_TRANSACTION], fetchMobileConfirmTransaction)
}

export default loadMobileConfirmTransactionSaga
