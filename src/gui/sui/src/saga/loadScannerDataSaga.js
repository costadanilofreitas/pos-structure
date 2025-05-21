import { takeEvery } from 'redux-saga/effects'
import { SCANNER_DATA } from '../constants/actionTypes'


function parseData(data) {
  return data.trim()
}

function fetchScannerData(action) {
  if (window.scanner != null) {
    window.scanner.sellByBarcode(parseData(action.payload['#text']))
  }
}

function* loadScannerDataSaga() {
  yield takeEvery([SCANNER_DATA], fetchScannerData)
}

export default loadScannerDataSaga
