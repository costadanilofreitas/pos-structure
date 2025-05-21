import { call, put, takeLatest } from 'redux-saga/effects'

import { MessageBus } from '3s-posui/core'
import { delay } from '3s-posui/utils'
import { RESYNC } from '3s-posui/constants/actionTypes'

import { FLOOR_PLAN_CHANGED, FLOOR_PLAN_LOADED } from '../constants/actionTypes'


function* fetchFloorPlan(posId) {
  const msgBus = new MessageBus(posId)
  const msgBusSyncAction = msgBus.syncAction.bind(msgBus)

  while (true) {
    try {
      const response = yield call(msgBusSyncAction, 'get_floor_plan')
      if (!response.ok) {
        console.error('Error loading floor plan. Response is not ok')
      } else if (response.data == null || response.data === '') {
        console.error('Error loading floor plan. Response data is empty or null')
      } else {
        yield put({ type: FLOOR_PLAN_LOADED, payload: response.data })
        return
      }
    } catch (e) {
      console.error(`Error loading floor plan: ${e}`)
    }

    yield call(delay, 1000)
  }
}

function* loadFloorPlanSaga(posId) {
  yield takeLatest([FLOOR_PLAN_CHANGED, RESYNC], fetchFloorPlan, posId)
}

export default loadFloorPlanSaga
