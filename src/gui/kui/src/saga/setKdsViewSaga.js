import _ from 'lodash'
import { call, takeLatest } from 'redux-saga/effects'

import { parseXml, xmlToJson } from '3s-posui/utils'

import MessageBus from '../util/MessageBus'
import { modelChangeKDS } from '../store/eventLoopMiddleware'
import { SET_KDS_VIEW } from '../constants/actionTypes'


function* setKdsView(kdsId, action) {
  const msgBus = new MessageBus(kdsId)
  const changeKDSView = msgBus.changeKDSView.bind(msgBus)

  let payload = null
  while (true) {
    try {
      const response = yield call(changeKDSView, action.payload)

      if (response == null || !response.ok) {
        console.error(`Error loading KDS Model data. Response: ${response}`)
      } else {
        payload = response.data
        const json = xmlToJson(parseXml(payload))
        if (_.has(json, 'KdsModel')) {
          yield call(modelChangeKDS, json.KdsModel)
        }
        break
      }
    } catch (e) {
      console.error(`Error loading KDS Model data. Exception: ${e}`)
    }
  }
}

function* setKdsViewSaga(posId) {
  yield takeLatest([SET_KDS_VIEW], setKdsView, posId)
}

export default setKdsViewSaga
