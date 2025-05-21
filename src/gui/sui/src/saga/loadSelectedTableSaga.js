import { call, put, takeLatest } from 'redux-saga/effects'

import { MessageBus } from '3s-posui/core'
import { delay } from '3s-posui/utils'
import { RESYNC } from '3s-posui/constants/actionTypes'

import { FETCH_SELECTED_TABLE, TABLE_SELECTED } from '../constants/actionTypes'


function* fetchSelectedTable(posId) {
  const msgBus = new MessageBus(posId)
  const msgBusSyncAction = msgBus.syncAction.bind(msgBus)

  while (true) {
    try {
      const response = yield call(msgBusSyncAction, 'getMyTable')
      if (!response.ok) {
        console.error('Error loading selected table. Response is not OK')
      } else if (response.data === '') {
        console.error('Error loading selected table. Response data is empty')
      } else {
        const payload = !_.isEmpty(response.data) ? response.data : ''
        yield put({ type: TABLE_SELECTED, payload: payload })
        return
      }
    } catch (e) {
      console.error('Error loading selected table')
    }

    yield call(delay, 1000)
  }
}

function* loadSelectedTableSaga(posId) {
  yield takeLatest([FETCH_SELECTED_TABLE, RESYNC], fetchSelectedTable, posId)
}

export default loadSelectedTableSaga
