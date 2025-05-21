import { put, call, takeLatest } from 'redux-saga/effects'

import { MessageBus } from '3s-posui/core'
import { delay } from '3s-posui/utils'
import { RESYNC } from '3s-posui/constants/actionTypes'

import { FETCH_TEF_AVAILABLE, TEF_AVAILABLE_CHANGED } from '../constants/actionTypes'


function* fetchTefAvailable(posId) {
  const msgBus = new MessageBus(posId)
  const msgBusSyncAction = msgBus.syncAction.bind(msgBus)

  while (true) {
    try {
      const response = yield call(msgBusSyncAction, 'is_tef_available')
      if (!response.ok) {
        console.error('Error loading TEF Available. Response is not OK')
      } else if (response.data === '') {
        console.error('Error loading TEF Available. Response data empty')
      } else {
        yield put({ type: TEF_AVAILABLE_CHANGED, payload: response.data })
        return
      }
    } catch (e) {
      console.error(`Error loading TEF Available exception: ${e.toString()}`)
    }

    yield call(delay, 1000)
  }
}

function* loadTefAvailableSaga(posId) {
  yield takeLatest([FETCH_TEF_AVAILABLE, RESYNC], fetchTefAvailable, posId)
}

export default loadTefAvailableSaga
