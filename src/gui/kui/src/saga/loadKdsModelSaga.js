import _ from 'lodash'
import { call, takeLatest } from 'redux-saga/effects'

import { delay, parseXml, xmlToJson } from '3s-posui/utils'
import { RESYNC } from '3s-posui/constants/actionTypes'

import MessageBus from '../util/MessageBus'
import { modelChangeKDS } from '../store/eventLoopMiddleware'
import { FETCH_KDS_MODEL } from '../constants/actionTypes'

function* sendRefresh(kdsId) {
  const msgBus = new MessageBus(kdsId)
  const sendKDSRefresh = msgBus.sendKDSRefresh.bind(msgBus)

  let refreshed = false
  while (!refreshed) {
    try {
      const response = yield call(sendKDSRefresh)

      if (response == null || !response.ok) {
        console.error(`Error sending Refresh message. Response: ${response}`)
      } else {
        refreshed = true
      }
    } catch (e) {
      console.error(`Error sending Refresh message. Exception: ${e}`)
    }

    yield call(delay, 5000)
  }
}

function* fetchKdsModelData(kdsId) {
  const msgBus = new MessageBus(kdsId)
  const getKdsModel = msgBus.getKDSModel.bind(msgBus)

  let payload = null
  while (payload == null) {
    try {
      const response = yield call(getKdsModel)

      if (response == null || !response.ok) {
        console.error(`Error loading KDS Model data. Response: ${response}`)
        payload = null
      } else {
        payload = response.data
        const json = xmlToJson(parseXml(payload))
        if (_.has(json, 'KdsModel')) {
          yield call(modelChangeKDS, json.KdsModel)
          yield call(sendRefresh, kdsId)
        }
      }
    } catch (e) {
      console.error(`Error loading KDS Model data. Exception: ${e}`)
    }
  }
}

function* loadKdsModelSaga(posId) {
  yield takeLatest([RESYNC, FETCH_KDS_MODEL], fetchKdsModelData, posId)
}

export default loadKdsModelSaga
