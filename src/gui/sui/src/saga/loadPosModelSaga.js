import { call, race, takeLatest } from 'redux-saga/effects'
import { MessageBus } from '3s-posui/core'
import { delay, xmlToJson, parseXml } from '3s-posui/utils'
import { RESYNC } from '3s-posui/constants/actionTypes'
import _ from 'lodash'
import { modelChangePOS } from '../store/eventLoopMiddleware'
import { FETCH_POS_MODEL } from '../constants/actionTypes'


function* fetchPosModelData(posId) {
  const msgBus = new MessageBus(posId)
  const getPosModel = msgBus.getPosModel.bind(msgBus)

  let payload = null
  while (payload == null) {
    try {
      const { response, timeout } = yield race({
        response: call(getPosModel),
        timeout: delay(5000)
      })

      if (timeout || response == null || !response.ok) {
        console.error(`Error loading POS Model data. Response: ${response} / Timeout: ${timeout}`)
      } else {
        payload = response.data
        const json = xmlToJson(parseXml(payload))
        if (_.has(json, 'PosModel')) {
          yield call(modelChangePOS, json.PosModel)
        }
      }
    } catch (e) {
      console.error(`Error loading POS Model data. Exception: ${e}`)
    }

    yield call(delay, 1000)
  }
}

function* loadPosModelSaga(posId) {
  yield takeLatest([FETCH_POS_MODEL, RESYNC], fetchPosModelData, posId)
}

export default loadPosModelSaga
