import { call, put, takeLatest } from 'redux-saga/effects'

import { MessageBus } from '3s-posui/core'
import { delay } from '3s-posui/utils'
import { RESYNC } from '3s-posui/constants/actionTypes'

import { FETCH_STATIC_CONFIG, STATIC_CONFIG_LOADED } from '../constants/actionTypes'


function* fetchStaticConfig(posId) {
  const msgBus = new MessageBus(posId)
  const msgBusSyncAction = msgBus.syncAction.bind(msgBus)

  while (true) {
    try {
      const response = yield call(msgBusSyncAction, 'get_static_config')
      if (!response.ok) {
        console.error('Error loading static config. Response is not OK')
      } else if (response.data == null || response.data === '') {
        console.error('Error loading static config. Response data is null or empty')
      } else {
        yield put({ type: STATIC_CONFIG_LOADED, payload: response.data })
        return
      }
    } catch (e) {
      console.error('Error loading static config')
    }

    yield call(delay, 1000)
  }
}

function* loadStaticConfigSaga(posId) {
  yield takeLatest([FETCH_STATIC_CONFIG, RESYNC], fetchStaticConfig, posId)
}

export default loadStaticConfigSaga
