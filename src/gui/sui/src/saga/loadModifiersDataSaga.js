import { put, call, takeLatest } from 'redux-saga/effects'
import _ from 'lodash'

import { MessageBus } from '3s-posui/core'
import { delay } from '3s-posui/utils'
import { MODIFIERS_LOADED, RESYNC } from '3s-posui/constants/actionTypes'
import { FETCH_MODIFIERS_DATA } from '../constants/actionTypes'


function* fetchModifiersData(posId) {
  const msgBus = new MessageBus(posId)
  const msgBusSyncAction = msgBus.syncAction.bind(msgBus)

  while (true) {
    try {
      const response = yield call(msgBusSyncAction, 'get_modifiers_data')
      if (!response.ok) {
        console.error('Error loading modifiers data. Response is not ok')
      } else if (!_.isObject(response.data)) {
        console.error('Error loading modifiers data. Response data is not an object')
      } else {
        yield put({ type: MODIFIERS_LOADED, payload: response.data || null })
        return
      }
    } catch (e) {
      console.error('Error loading modifiers data')
    }

    yield call(delay, 1000)
  }
}

function* loadModifiersDataSaga(posId) {
  yield takeLatest([FETCH_MODIFIERS_DATA, RESYNC], fetchModifiersData, posId)
}

export default loadModifiersDataSaga
