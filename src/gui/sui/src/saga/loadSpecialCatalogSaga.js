import { call, put, takeLatest } from 'redux-saga/effects'

import { MessageBus } from '3s-posui/core'
import { delay } from '3s-posui/utils'
import { RESYNC } from '3s-posui/constants/actionTypes'

import { FETCH_SPECIAL_CATALOG, SPECIAL_CATALOG_LOADED } from '../constants/actionTypes'


function* fetchSpecialCatalog(posId) {
  const msgBus = new MessageBus(posId)
  const msgBusSyncAction = msgBus.syncAction.bind(msgBus)

  while (true) {
    try {
      const response = yield call(msgBusSyncAction, 'get_special_catalog')
      if (!response.ok) {
        console.error('Error loading special catalog. Response is not OK')
      } else if (response.data === '') {
        console.error('Error loading special catalog. Response data is empty')
      } else {
        yield put({ type: SPECIAL_CATALOG_LOADED, payload: response.data })
        return
      }
    } catch (e) {
      console.error('Error loading special catalog')
    }

    yield call(delay, 1000)
  }
}

function* loadSpecialCatalogSaga(posId) {
  yield takeLatest([FETCH_SPECIAL_CATALOG, RESYNC], fetchSpecialCatalog, posId)
}

export default loadSpecialCatalogSaga
