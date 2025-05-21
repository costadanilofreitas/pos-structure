import { put, call, takeEvery } from 'redux-saga/effects'
import { MessageBus } from '../core'
import {
  EXECUTE_ACTION, EXECUTE_ACTION_REQUESTED, EXECUTE_ACTION_SUCCEEDED, EXECUTE_ACTION_FAILED
} from '../constants/actionTypes'


function* executeAction(msgBusAction, action) {
  const payload = action.payload
  try {
    yield put({ type: EXECUTE_ACTION_REQUESTED, payload })
    const response = yield call(msgBusAction, action.payload.actionName, ...action.payload.params)
    yield put({ type: EXECUTE_ACTION_SUCCEEDED, payload: { ...payload, ...response } })
  } catch (e) {
    yield put({ type: EXECUTE_ACTION_FAILED, payload: { ...payload, message: e.message } })
  }
}

function* executeSaga(posId) {
  const msgBus = new MessageBus(posId)
  const msgBusAction = msgBus.action.bind(msgBus)
  yield takeEvery(EXECUTE_ACTION, executeAction, msgBusAction)
}

export default executeSaga
