import { call, put, takeLatest } from 'redux-saga/effects'

import { MessageBus } from '3s-posui/core'
import { delay } from '3s-posui/utils'
import { NAVIGATION_DATA_LOADED, RESYNC } from '3s-posui/constants/actionTypes'
import { FETCH_NAVIGATION_DATA } from '../constants/actionTypes'


function* fetchNavigationData(posId) {
  const msgBus = new MessageBus(posId)
  const msgBusSyncAction = msgBus.syncAction.bind(msgBus)

  while (true) {
    try {
      const response = yield call(msgBusSyncAction, 'get_navigation_data')
      if (!response.ok) {
        console.error('Error loading navigation data. Response is not OK')
      } else if (!Array.isArray(response.data)) {
        console.error('Error loading navigation data. Response data is not an array')
      } else {
        yield put({ type: NAVIGATION_DATA_LOADED, payload: response.data || null })
        return
      }
    } catch (e) {
      console.error('Error loading navigation data')
    }

    yield call(delay, 1000)
  }
}

function* loadNavigationDataSaga(posId) {
  yield takeLatest([FETCH_NAVIGATION_DATA, RESYNC], fetchNavigationData, posId)
}

export default loadNavigationDataSaga
