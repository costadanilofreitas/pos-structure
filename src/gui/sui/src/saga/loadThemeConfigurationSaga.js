import { call, put, takeLatest } from 'redux-saga/effects'
import { delay } from '3s-posui/utils'
import { RESYNC } from '3s-posui/constants/actionTypes'
import axios from 'axios'

import { FETCH_THEME_CONFIGURATION, THEME_CONFIGURATION_CHANGED } from '../constants/actionTypes'

function getThemeConfiguration() {
  return axios.get('/sui/static/themeConfig.json')
    .then(response => response.data)
    .catch(e => console.error(e))
}


function* fetchThemeConfiguration() {
  while (true) {
    try {
      const response = yield call(getThemeConfiguration)
      yield put({ type: THEME_CONFIGURATION_CHANGED, payload: response })
      return
    } catch (e) {
      console.error(`Error loading Theme Configuration exception: ${e.toString()}`)
    }

    yield call(delay, 1000)
  }
}

function* loadThemeConfigurationSaga() {
  yield takeLatest([FETCH_THEME_CONFIGURATION, RESYNC], fetchThemeConfiguration)
}

export default loadThemeConfigurationSaga
