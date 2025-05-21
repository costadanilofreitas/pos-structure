import axios from 'axios'
import _ from 'lodash'
import { call, fork, put } from 'redux-saga/effects'

import { delay, ensureArray, toBoolean, xmlToJson } from '3s-posui/utils'
import * as types from '3s-posui/constants/actionTypes'
import convertProdOrder from '3s-posui/utils/prod'

const API_START_URL = '/mwapp/events/start'
const API_LISTEN_URL = '/mwapp/events/listen'

const defaultHeaders = {
  'Accept': 'application/json',
  'Content-Type': 'application/json'
}

const listenEvent = (kdsId, evtType, syncId = null) => {
  const timeStamp = (new Date()).getTime()
  const syncIdText = syncId == null ? '' : `&syncId=${syncId}`
  const mainUrl = syncId == null ? API_START_URL : API_LISTEN_URL

  return axios.get(`${mainUrl}?subject=${evtType}${kdsId}${syncIdText}&_ts=${timeStamp}`, {
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

function orderKdsEvents(events) {
  events.sort((a, b) => {
    if (_.has(a, 'RefreshEnd')) {
      return 1
    }
    return (_.has(b, 'RefreshEnd')) ? -1 : 0
  })
}

function getTimeInSeconds(time) {
  const timeRef = time.split(':')

  return timeRef.reduce(
    (totalTime, currentUnitQuantity, currentIndex) =>
      (totalTime) + (currentUnitQuantity * (60 ** (3 - currentIndex - 1))),
    0
  )
}

export function* modelChangeKDS(events) {
  const keys = Object.keys(events)

  for (let i = 0; i < keys.length; i++) {
    const key = keys[i]
    switch (key) {
      case '@attributes':
      case '#text':
        break
      case 'Language': {
        yield put({
          type: types.LANGUAGE_CHANGED,
          payload: { language: events[key]['@attributes'].name }
        })
        break
      }
      case 'Title': {
        yield put({
          type: types.KDS_TITLE,
          payload: events[key]['@attributes'].name
        })
        break
      }
      case 'ViewUpdate': {
        const event = events[key]
        if (event['@attributes'] == null) {
          break
        }

        const productionView = event['@attributes'].name
        const prodOrder = convertProdOrder(event)
        yield put({ type: types.PROD_VIEW_UPDATE, payload: { key: productionView, value: prodOrder } })
        yield put({ type: types.PROD_VIEW_UPDATE_FINISHED, payload: productionView })
        break
      }
      case 'Views': {
        const views = ensureArray(events.Views.View)
        const currentView = views.find(x => x['@attributes'].selected === 'true')
        const viewKeys = Object.keys(currentView)
        const currentViewModel = {}

        for (let k = 0; k < viewKeys.length; k++) {
          const viewKey = viewKeys[k]
          switch (viewKey) {
            case '@attributes':
            case '#text':
              break
            case 'Layout': {
              const attrs = currentView[viewKey]['@attributes'] || {}
              const layout = {}
              _.forEach(_.keys(attrs), (index) => {
                if (index === 'fontsize') {
                  layout[index] = parseFloat(attrs[index])
                } else {
                  layout[index] = parseInt(attrs[index], 10)
                }
              })
              yield put({
                type: types.KDS_LAYOUT,
                payload: layout
              })

              currentViewModel.Layout = layout
              break
            }
            case 'Title': {
              yield put({
                type: types.KDS_VIEW_TITLE,
                payload: currentView[viewKey]['@attributes'].value
              })
              break
            }
            case 'CellFormat': {
              const cellFormat = currentView[viewKey]['@attributes'] || {}
              yield put({
                type: types.KDS_CELL_FORMAT,
                payload: cellFormat
              })
              break
            }
            case 'Settings': {
              const settings = currentView[viewKey] || { Setting: [] }
              const settingList = ensureArray(settings.Setting)
              const settingsConfig = {}
              _.forEach(settingList, (setting) => {
                settingsConfig[setting['@attributes'].name] = setting['@attributes'].value
              })

              yield put({
                type: types.KDS_SETTINGS,
                payload: settingsConfig
              })
              break
            }
            case 'Thresholds': {
              const rawThresholds = ensureArray(currentView[viewKey].Threshold || [])
              const parsedThresholds = rawThresholds.map(rawThreshold => {
                const [time, color] = rawThreshold['@attributes'].value.split('#')
                return {
                  time: getTimeInSeconds(time),
                  color: `#${color}`
                }
              }).sort((a, b) => a.time < b.time)
              yield put({
                type: types.KDS_THRESHOLDS,
                payload: parsedThresholds
              })
              break
            }
            case 'Statistics': {
              const rawStatistics = ensureArray(currentView[viewKey].Statistic || [])
              currentView.parsedStatistics = rawStatistics.map(rawStatistic => {
                const { name, format } = rawStatistic['@attributes']
                return { name, format }
              })

              break
            }
            case 'AutoOrderCommand': {
              const { command, time } = currentView[viewKey]['@attributes']
              const parsedCommand = {
                command,
                time: getTimeInSeconds(time)
              }
              yield put({
                type: types.KDS_AUTO_ORDER_COMMANDS,
                payload: parsedCommand
              })
              break
            }
            case 'Carousel': {
              yield put({
                type: types.KDS_CAROUSEL,
                payload: toBoolean(currentView[viewKey]['@attributes'].state, true)
              })
              break
            }
            case 'ShowItems': {
              yield put({
                type: types.KDS_SHOW_ITEMS,
                payload: toBoolean(currentView[viewKey]['@attributes'].state, true)
              })
              break
            }
            case 'SelectedZoom': {
              yield put({
                type: types.KDS_SELECTED_ZOOM,
                payload: parseInt(currentView[viewKey]['@attributes'].value, 10)
              })
              break
            }
            case 'DisplayMode': {
              yield put({
                type: types.KDS_DISPLAY_MODE,
                payload: currentView[viewKey]['@attributes'].value
              })
              break
            }
            case 'ColoredArea': {
              yield put({
                type: types.KDS_COLORED_AREA,
                payload: currentView[viewKey]['@attributes'].area
              })
              break
            }
            case 'ViewWithActions': {
              yield put({
                type: types.VIEW_WITH_ACTIONS,
                payload: currentView[viewKey]['@attributes'].value
              })
              break
            }
            default: {
              break
            }
          }
        }

        const viewsObjects = views.map(function (view) {
          return {
            name: view['@attributes'].name,
            title: view.Title['@attributes'].value,
            selected: view['@attributes'].selected === 'true',
            statistics: view.parsedStatistics,
            productionView: view.ProductionView['@attributes'].value
          }
        })

        yield put({
          type: types.KDS_VIEWS_MODEL,
          payload: viewsObjects
        })

        break
      }
      case 'RefreshEnd': {
        yield put({ type: types.KDS_REFRESH_END })
        break
      }
      case 'BumpBar': {
        const currentBumpBar = events[key].BumpBar
        if (currentBumpBar == null) {
          break
        }

        const commands = _.fromPairs(
          ensureArray(currentBumpBar.Command || []).map((cmd) => [
            _.toLower(cmd['@attributes'].name),
            (cmd['@attributes'].value || '').split(/[.|/\\]/)
          ])
        )
        const simulateBumpBar = currentBumpBar['@attributes'].simulate.toLowerCase() === 'true'
        const bumpBar = { name: currentBumpBar['@attributes'].name, commands, simulate: simulateBumpBar }

        yield put({
          type: types.KDS_BUMPBARS,
          payload: { bumpbar: bumpBar }
        })
        break
      }
      case 'Reload': {
        yield put({ type: types.RESYNC })
        break
      }
      case 'Command': {
        yield put({
          type: types.KDS_COMMAND,
          payload: events[key] || {}
        })
        break
      }
      case 'ModifierPrefixes': {
        const result = {}
        const prefixes = ensureArray(events[key].Prefix || [])
        _.forEach(prefixes, (prefix) => {
          result[prefix['@attributes'].name] = prefix['@attributes'].value
        })

        yield put({
          type: types.KDS_MODIFIER_PREFIXES,
          payload: result
        })

        break
      }
      case 'Statistics': {
        if (events[key]['@attributes'].text != null) {
          yield put({
            type: types.KDS_STATISTICS,
            payload: JSON.parse(events[key]['@attributes'].text)
          })
        }
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
        yield call(delay, 1000)

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
            const json = xmlToJson(response.xml)
            if (_.has(json, 'Events') && _.has(json.Events, 'Event')) {
              const events = ensureArray(json.Events.Event)
              orderKdsEvents(events)

              for (let i = 0; i < events.length; i++) {
                yield call(modelChangeKDS, events[i])
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
      yield call(delay, 1000)
      yield put({ type: types.RESYNC })
    }
  }
}

export default function* eventLoopMiddleware(kdsId = null) {
  if (!kdsId) {
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

  yield fork(pollForEventsLoop, kdsId, 'KDS')
}
