import _ from 'lodash'
import { call, takeLatest } from 'redux-saga/effects'

import { parseXml, xmlToJson } from '3s-posui/utils'

import MessageBus from '../util/MessageBus'
import { modelChangeKDS } from '../store/eventLoopMiddleware'
import { SET_KDS_ZOOM } from '../constants/actionTypes'


function* setKdsZoom(kdsId, action) {
  const msgBus = new MessageBus(kdsId)
  const changeKDSZoom = msgBus.sendKDSChangeZoom.bind(msgBus)

  let payload = null
  try {
    const response = yield call(changeKDSZoom, action.payload)

    if (response == null || !response.ok) {
      console.error(`Error loading KDS Model data. Response: ${response}`)
    } else {
      payload = response.data
      const json = xmlToJson(parseXml(payload))
      if (_.has(json, 'KdsModel')) {
        yield call(modelChangeKDS, json.KdsModel)
      }
    }
  } catch (e) {
    console.error(`Error loading KDS Model data. Exception: ${e}`)
  }
}

function* setKdsZoomSaga(posId) {
  yield takeLatest([SET_KDS_ZOOM], setKdsZoom, posId)
}

export default setKdsZoomSaga
