import { takeEvery } from 'redux-saga/effects'
import DialogType from '../constants/DialogType'
import { MOBILE_PRINT } from '../constants/actionTypes'


function handleProcessPrint(status, message, payload) {
  if (status !== '0' && status !== 0) {
    console.error(`${message} - ${payload}`)
    if (status === '240' || status === 240) {
      this.props.showDialog({
        title: '$WARNING',
        type: DialogType.Alert,
        message: '$DEVICE_NOT_INITIALIZED'
      })
    }
  }
}

function fetchMobilePrint(action) {
  if (window.mwapi != null && window.processPrintCallback == null) {
    window.processPrintCallback = handleProcessPrint
  }
  if (window.mwapi != null) {
    window.mwapi.print('processPrintCallback', action.payload['#text'])
  } else {
    console.error('Device not initialized')
  }
}

function* loadMobilePrintSaga() {
  if (window.mwapi != null) {
    window.processPrintCallback = handleProcessPrint
  }

  yield takeEvery([MOBILE_PRINT], fetchMobilePrint)
}

export default loadMobilePrintSaga
