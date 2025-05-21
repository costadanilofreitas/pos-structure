import _ from 'lodash'
import { call, put, select, takeLatest } from 'redux-saga/effects'
import { MessageBus } from '3s-posui/core'
import { delay } from '3s-posui/utils'
import { ABANDON_POS, CHANGE_MENU, TABLE_SELECTED } from '../constants/actionTypes'


const order = state => state.order
const table = state => state.selectedTable

function* doAbandonPos(posId) {
  try {
    const msgBus = new MessageBus(posId)
    const msgBusSyncAction = msgBus.syncAction.bind(msgBus)

    const activeOrder = yield select(order)
    if (activeOrder) {
      if (_.includes(['IN_PROGRESS', 'TOTALED'], activeOrder.state)) {
        yield call(msgBusSyncAction, 'handle_void_order', 9, 'false', '', 'false')
        yield call(delay, 800)
      }
    }
    const myTable = yield select(table)
    if (myTable) {
      yield put({ type: TABLE_SELECTED, payload: null })
      yield call(msgBusSyncAction, 'deselect_table')
    }
    yield put({ type: CHANGE_MENU, payload: null })
    yield call(msgBusSyncAction, 'pause_user')
  } catch (e) {
    console.error('Error on abandonPoS')
  }
}

function* abandonPos(posId) {
  yield takeLatest(ABANDON_POS, doAbandonPos, posId)
}

export default abandonPos
