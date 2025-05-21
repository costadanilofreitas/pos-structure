import { takeLatest, put, call } from 'redux-saga/effects'
import { MessageBus } from '../core'
import { delay } from '../utils'
import { I18N_LOADED, I18N_FETCH_SUCCEEDED, I18N_FETCH_FAILED, LANGUAGE_CHANGED } from '../constants/actionTypes'

function* fetchI18N(action) {
  try {
    const msgBus = new MessageBus()
    const language = action.payload.language
    const i18n = yield call(msgBus.sendGetI18nMessage.bind(msgBus), language)
    yield put({ type: I18N_FETCH_SUCCEEDED, payload: { messages: i18n.data, language: language } })
    // Dispatch the "loaded" action after a short delay. This is to ensure that the
    // intl-react provider has updated its internal dictionary
    yield call(delay, 200)
    yield put({ type: I18N_LOADED })
  } catch (e) {
    yield put({ type: I18N_FETCH_FAILED, payload: { message: e.message } })
  }
}

function* i18nSaga() {
  yield takeLatest(LANGUAGE_CHANGED, fetchI18N)
}

export default i18nSaga
