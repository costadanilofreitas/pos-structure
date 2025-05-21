import axios from 'axios'
import _ from 'lodash'
import { call, fork, put, select } from 'redux-saga/effects'

import { delay, ensureArray, normalizeOrder, xmlToJson } from '3s-posui/utils'
import * as types from '3s-posui/constants/actionTypes'
import { SET_OPERATOR_LEVEL } from '../constants/actionTypes'

const API_START_URL = '/mwapp/events/start'
const API_LISTEN_URL = '/mwapp/events/listen'

const getCurrentOrder = (state) => state.order
const getDrawerState = (state) => state.drawerState
const getDrawerOpened = (state) => state.drawerOpened


const listenEvent = (posId, evtType, syncId = null) => {
  const timeStamp = (new Date()).getTime()
  const syncIdText = syncId == null ? '' : `&syncId=${syncId}`
  const mainUrl = syncId == null ? API_START_URL : API_LISTEN_URL
  const defaultHeaders = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  }

  return axios.get(`${mainUrl}?subject=${evtType}${posId}${syncIdText}&_ts=${timeStamp}`, {
    headers: defaultHeaders,
    responseType: 'document'
  })
    .then(response => {
      const serverTime = response.headers.date
      const timeDelta = serverTime ? (new Date(serverTime) - new Date()) : 0
      return {
        ok: true,
        syncId: response.headers['x-sync-id'],
        xml: response.data,
        timeDelta
      }
    }, error => {
      const conflict = error.response && error.response.headers['x-conflicted'] === 'true'
      if (conflict) {
        console.warn(`A conflict was detected. Check if this ${evtType} is not opened anywhere else.`)
      } else {
        console.warn('Error while listening for an event')
      }
      return { ok: false }
    })
}

export function* modelChangePOS(events) {
  const keys = Object.keys(events)

  for (let i = 0; i < keys.length; i++) {
    const key = keys[i]

    switch (key) {
      case '@attributes':
      case '#text':
        // these two are ignored on purpose
        break
      case 'Language': {
        yield put({
          type: types.LANGUAGE_CHANGED,
          payload: { language: events[key]['@attributes'].name }
        })
        break
      }
      case 'PosState': {
        yield put({ type: types.POS_STATE_CHANGED, payload: events[key]['@attributes'] })
        break
      }
      case 'Operator': {
        const operator = events[key]['@attributes']
        yield put({ type: types.OPERATOR_CHANGED, payload: operator })
        break
      }
      case 'Operators': {
        if (_.isEmpty(events[key])) {
          yield put({ type: types.OPERATOR_CHANGED, payload: undefined })
        } else {
          yield put({ type: SET_OPERATOR_LEVEL, payload: events[key] })
        }

        break
      }
      case 'Screen': {
        yield put({ type: types.SCREEN_CHANGED, payload: events[key]['@attributes'] })
        break
      }
      case 'CashDrawerStatus': {
        yield put({ type: types.CASH_DRAWER_CHANGED, payload: { status: events[key]['#text'] } })
        break
      }
      case 'CashDrawer': {
        yield put({ type: types.CASH_DRAWER_CHANGED, payload: events[key]['@attributes'] })
        break
      }
      case 'CurrentOrder': {
        const previousOrder = yield select(getCurrentOrder)
        const order = normalizeOrder(events[key].Order)
        yield put({ type: types.ORDER_CHANGED, payload: order })

        const timeStamp = (new Date()).getTime()
        yield put({ type: types.ORDER_CHANGED_LAST_TIMESTAMP, payload: timeStamp })

        const previousState = ((previousOrder || {})['@attributes'] || {}).state
        const currentState = ((order || {})['@attributes'] || {}).state
        if (previousState !== 'PAID' && currentState === 'PAID') {
          yield put({ type: types.ORDER_PAID })

          const drawerState = Boolean(yield select(getDrawerState))
          const drawerOpened = Boolean(yield select(getDrawerOpened))
          if (drawerState !== drawerOpened) {
            const statusText = (drawerState) ? 'OPENED' : 'CLOSED'
            yield put({ type: types.FORCE_CASH_DRAWER_CHANGE, payload: { status: statusText } })
          }
        }
        if (previousState !== 'STORED' && currentState === 'STORED') {
          yield put({ type: types.ORDER_STORED })
        }
        if (!_.includes(['IN_PROGRESS', 'TOTALED'], previousState) && currentState === 'IN_PROGRESS') {
          yield put({ type: types.ORDER_STARTED })
        }
        break
      }
      case 'InfoMessage': {
        yield put({ type: types.INFO_MESSAGE_CHANGED, payload: events[key]['@attributes'] })
        break
      }
      case 'Custom': {
        const customProps = ensureArray(events[key])
        const custom = {}

        const validProps = customProps.filter((prop) => {
          return _.has(prop, '@attributes') && _.has(prop['@attributes'], 'name')
        })
        validProps.forEach((prop) => {
          custom[prop['@attributes'].name] = prop['@attributes'].value
        })

        yield put({ type: types.CUSTOM_CHANGED, payload: custom })
        break
      }
      case 'WorkingMode': {
        yield put({ type: types.MODE_CHANGED, payload: events[key]['@attributes'] })
        break
      }
      case 'UsedServices': {
        let services = []
        if (_.has(events[key], 'Service')) {
          const servicesList = ensureArray(events[key].Service)
          services = servicesList.map((service) => service['@attributes'])
        }
        yield put({ type: types.SERVICES_CHANGED, payload: services })
        break
      }
      case 'ModifiersData': {
        let modifiers = {}
        try {
          modifiers = JSON.parse(((events[key].modifiersData || {})['#cdata-section']) || '{}')
        } catch (e) {
          console.error(`Error on the ModifiersData parse - ERROR: ${e}`)
        }

        yield put({ type: types.MODIFIERS_DATA_CHANGED, payload: modifiers })
        break
      }
      case 'RecallData': {
        const recallData = events[key] || {}
        const orders = []
        ensureArray((recallData.Orders || {}).Order || []).forEach(order => {
          orders.push(normalizeOrder(order))
        })

        recallData.Orders = orders
        yield put({ type: types.RECALL_DATA_CHANGED, payload: recallData })
        break
      }
      case 'PosDialog': {
        const dialogs = []
        const dialogsList = ensureArray(events[key]).filter((dialog) => {
          return dialog['@attributes'] && (dialog.DialogBox || {})['@attributes']
        })

        dialogsList.forEach((dialog) => {
          const att = dialog['@attributes']
          const box = (dialog.DialogBox || {})['@attributes']
          dialogs.push({
            id: att.id,
            timeout: att.timeout,
            type: box.type,
            title: box.title,
            message: box.message,
            info: box.info,
            btn: box.btn.split('|'),
            icon: box.icon,
            mask: box.mask,
            default: box.default,
            min: box.min,
            max: box.max,
            lineFeed: box.lineFeed,
            focus: box.focus,
            custom_dlg_id: box.custom_dlg_id,
            custom_dlg_timeout: box.custom_dlg_timeout,
            contents: (dialog.DialogBox || {}).Contents
          })
        })
        yield put({ type: types.DIALOGS_CHANGED, payload: dialogs })
        break
      }
      case 'CloseDialogBox': {
        const dialogsToClose = ensureArray(events[key])
        for (let j = 0; j < dialogsToClose.length; j++) {
          const dialog = dialogsToClose[j]
          const dlg = dialog['@attributes'] || {}
          if (dlg.id) {
            yield put({ type: types.DIALOG_CLOSED, payload: dlg.id })
          }
        }
        break
      }
      case 'ActionResult': {
        const event = events[key]
        const data = (event['#text']) ? atob(event['#text']) : ''

        yield put({
          type: types.EXECUTE_ACTION_FINISHED,
          payload: {
            ...event['@attributes'],
            data
          }
        })
        break
      }
      default: {
        // Custom Event
        yield put({ type: types.CUSTOM_EVENT, payload: { [key]: events[key] } })
        break
      }
    }
  }
}

function* pollForEventsLoop(posId, evtType) {
  let syncId = null
  while (true) {
    try {
      const response = yield call(listenEvent, posId, evtType, syncId)
      if (!response.ok) {
        yield put({
          type: types.EVENT_LOOP_STATE,
          payload: { syncId: null, conflict: !!response.conflict }
        })

        console.error(`Error on the listen event - RESPONSE: ${JSON.stringify(response)}`)
        yield call(delay, 5000)

        if (syncId != null) {
          yield put({ type: types.RESYNC })
        }
        syncId = null
      } else {
        syncId = response.syncId
        yield put({
          type: types.EVENT_LOOP_STATE,
          payload: { syncId: syncId, conflict: false }
        })

        if (response.timeDelta) {
          yield put({
            type: types.TIME_DELTA,
            payload: response.timeDelta
          })
        }

        if (response.xml) {
          try {
            // Convert the order picture XML received into a json object
            const json = xmlToJson(response.xml)
            if (_.has(json, 'Events') && _.has(json.Events, 'Event')) {
              const events = ensureArray(json.Events.Event)
              for (let i = 0; i < events.length; i++) {
                yield call(modelChangePOS, events[i])
              }
            }
          } catch (e) {
            console.error(`Error on the event parse - ERROR: ${e}`)
          }
        }
      }
    } catch (e) {
      syncId = null
      console.error(`Error on the event loop - ERROR: ${e}`)
      yield call(delay, 5000)
      yield put({ type: types.RESYNC })
    }
  }
}

export default function* eventLoopMiddleware(posId = null) {
  if (posId == null) {
    console.error('Invalid URL received, event loop not started')
    return
  }

  try {
    const oldSend = XMLHttpRequest.prototype.send
    XMLHttpRequest.prototype.send = function () {
      this.onabort = this.onerror
      oldSend.apply(this, arguments)
    }
  } catch (e) {
    console.error(`Error on XMLHttpRequest - ERROR: ${e}`)
  }

  yield fork(pollForEventsLoop, posId, 'POS')
}
