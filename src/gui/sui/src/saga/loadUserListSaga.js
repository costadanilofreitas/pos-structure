import { put, call, takeLatest, race } from 'redux-saga/effects'
import _ from 'lodash'

import { MessageBus } from '3s-posui/core'
import { delay, xmlToJson, parseXml } from '3s-posui/utils'
import { RESYNC } from '3s-posui/constants/actionTypes'

import { FETCH_USER_DATA, USER_DATA_LOADED } from '../constants/actionTypes'
import { ensureArray } from '../util/renderUtil'


function* fetchUserList(posId) {
  const msgBus = new MessageBus(posId)
  const msgBusSyncAction = msgBus.syncAction.bind(msgBus)

  let payload = null
  while (payload == null) {
    try {
      const { response, timeout } = yield race({
        response: call(msgBusSyncAction, 'get_user_list'),
        timeout: delay(5000)
      })

      if (timeout || response == null || !response.ok || response.data === '') {
        console.error(`Error loading user list. Response: ${response} / Timeout: ${timeout}`)
      } else {
        const xmlData = xmlToJson(parseXml(response.data))
        if ((xmlData != null) && (xmlData.UserInfo != null) && (xmlData.UserInfo.user != null)) {
          const userList = ensureArray(xmlData.UserInfo.user)
          const userObject = {}
          userList.forEach(user => {
            if (_.has(user, '@attributes')) {
              Object.keys(user['@attributes']).forEach(k => {
                user[k] = user['@attributes'][k]
              })
            }

            delete user['@attributes']
            userObject[user.UserId] = user
          })

          payload = userObject
          yield put({ type: USER_DATA_LOADED, payload })
        }
      }
    } catch (e) {
      console.error('Error loading user list')
    }

    yield call(delay, 1000)
  }
}

function* loadUserListSaga(posId) {
  yield takeLatest([FETCH_USER_DATA, RESYNC], fetchUserList, posId)
}

export default loadUserListSaga

