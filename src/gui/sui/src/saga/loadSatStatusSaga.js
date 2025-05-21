import { call, put, takeLatest, select } from 'redux-saga/effects'

import { MessageBus } from '3s-posui/core'
import { delay } from '3s-posui/utils'
import { RESYNC } from '3s-posui/constants/actionTypes'

import { FETCH_SAT_STATUS, SAT_STATUS_CHANGED } from '../constants/actionTypes'

const staticConfig = state => state.staticConfig
const mobileConfig = state => state.mobile
let fetchTimeout = 60000


function* fetchSatStatus(posId) {
  try {
    const myStaticConfig = yield select(staticConfig)
    const mobile = yield select(mobileConfig)

    if (mobile || myStaticConfig == null || myStaticConfig.satInfo == null || !myStaticConfig.satInfo.enabled) {
      yield put({ type: SAT_STATUS_CHANGED, payload: { 'enabled': false, 'working': false } })
      return
    }

    if (myStaticConfig && myStaticConfig.satInfo.timeout) {
      fetchTimeout = myStaticConfig.satInfo.timeout * 1000
    }

    const msgBus = new MessageBus(posId)
    const msgBusSyncAction = msgBus.syncAction.bind(msgBus)

    const response = yield call(msgBusSyncAction, 'get_sat_status', false)
    let working = false

    if (response != null && response.data != null && response.data.toLowerCase() === 'true') {
      working = true
    }

    yield put({ type: SAT_STATUS_CHANGED,
      payload: { 'enabled': true, 'working': working } })
  } catch (e) {
    console.error(`Error getting sat status:${e}`)
  }
}

export function* loadSatStatusSaga(posId) {
  yield takeLatest([FETCH_SAT_STATUS, RESYNC], fetchSatStatus, posId)
}

export function* reloadSatStatusSaga() {
  let condition = true
  while (condition) {
    try {
      yield put({ type: FETCH_SAT_STATUS, payload: null })
      yield call(delay, fetchTimeout)
    } catch (error) {
      condition = false
      console.error('Error fetching sat status')
    }
  }
}
