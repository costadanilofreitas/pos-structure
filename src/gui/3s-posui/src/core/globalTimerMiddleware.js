import { put, call, fork, take } from 'redux-saga/effects'
import { delay } from '../utils'
import { GLOBAL_TIMER_TICK, GLOBAL_TIMER_STOP } from '../constants/actionTypes'

let started = false

function* startGlobalTimer() {
  const startDate = Date.now()

  while (true) {
    const currentDate = Date.now()
    yield put({ type: GLOBAL_TIMER_TICK, payload: currentDate - startDate })
    yield call(delay, 1000)

    if (!started) {
      break
    }
  }
}

function* globalTimerMiddleware() {
  started = true
  yield fork(startGlobalTimer)
  yield take(GLOBAL_TIMER_STOP)
  started = false
}

export default globalTimerMiddleware
