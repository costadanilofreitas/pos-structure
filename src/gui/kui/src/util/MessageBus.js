import axios from 'axios'
import Base64 from 'base64-js'

const TK_KDS_GETMODEL = '0xF0B00001'
const TK_KDS_REFRESH = '0xF0B00003'
const TK_KDS_SET_PROD_STATE = '0xF0B00005'
const TK_KDS_UNDO_SERVE = '0xF0B00006'
const TK_KDS_TOGGLE_TAG_LINE = '0xF0B00008'
const TK_KDS_CHANGE_VIEW = '0xF0B0000A'
const TK_KDS_BUMP_BAR_COMMAND = '0xF0B0000B'
const TK_KDS_BUMP_ZOOM_NEXT = '0xF0B0000C'

const FM_PARAM = 0x00000002
const FM_STRING = 0x00000006

const KDS_CONTROLLER = 'NKDSCTRL'

class MessageBus {
  constructor(kdsId = 0) {
    this.kdsId = kdsId
  }

  sendMessage = (service, serviceType, token, format = FM_STRING, timeout = -1, data = '', sendB64 = false) => {
    const timeStamp = (new Date()).getTime()
    const isFirefox = 'InstallTrigger' in window

    let isBase64 = sendB64
    if (!isBase64 && data.indexOf('\0') !== -1 && isFirefox) {
      isBase64 = true
    }

    const isBase64Str = (isBase64) ? 'true' : 'false'
    const queryString = `?token=${token}&format=${format}&timeout=${timeout}&isBase64=${isBase64Str}&_ts=${timeStamp}`
    const url = `/mwapp/services/${serviceType}/${service}${queryString}`
    let data64 = null
    if (isBase64) {
      const len = data.length
      const byteArray = new Uint8Array(len)
      for (let i = 0; i < len; i++) {
        // eslint-disable-next-line no-bitwise
        byteArray.push(data.charCodeAt(i) & 0xFF)
      }
      data64 = Base64.fromByteArray(byteArray)
    }
    return axios.post(url, (isBase64) ? data64 : data)
      .then(response => {
        return { 'ok': true, 'data': response.data }
      }, (error) => {
        console.error(`Axios Exception - ${error} - URL: (${url})`)
        return { 'ok': false }
      })
  }

  getKDSModel() {
    const data = String(this.kdsId)
    return this.sendMessage(KDS_CONTROLLER, KDS_CONTROLLER, TK_KDS_GETMODEL, FM_STRING, 5000, data)
  }

  changeKDSView(view) {
    const viewName = view != null ? view : ''
    const data = `${String(this.kdsId)}\0${viewName}`
    return this.sendMessage(KDS_CONTROLLER, KDS_CONTROLLER, TK_KDS_CHANGE_VIEW, FM_STRING, 5000, data)
  }

  sendKDSRefresh() {
    return this.sendMessage(KDS_CONTROLLER, KDS_CONTROLLER, TK_KDS_REFRESH, FM_STRING, 5000, String(this.kdsId))
  }

  sendKDSSetState(orderId, state, view) {
    const data = `${this.kdsId}\0${orderId}\0${state}\0${view}`
    return this.sendMessage(KDS_CONTROLLER, KDS_CONTROLLER, TK_KDS_SET_PROD_STATE, FM_PARAM, 5000, data)
  }

  sendKDSUndoServe(view) {
    const data = `${this.kdsId}\0${view}`
    return this.sendMessage(KDS_CONTROLLER, KDS_CONTROLLER, TK_KDS_UNDO_SERVE, FM_PARAM, 5000, data)
  }

  sendKDSBumpBarEvent(name, code) {
    const data = `${this.kdsId}\0${name}\0${code}`
    return this.sendMessage(KDS_CONTROLLER, KDS_CONTROLLER, TK_KDS_BUMP_BAR_COMMAND, FM_PARAM, 5000, data)
  }

  sendKDSChangeZoom(view) {
    const data = `${this.kdsId}\0${view}`
    return this.sendMessage(KDS_CONTROLLER, KDS_CONTROLLER, TK_KDS_BUMP_ZOOM_NEXT, FM_PARAM, 5000, data)
  }

  sendKDSToggleTagLine(orderId, lineNumber, view) {
    const data = `${this.kdsId}'\0'${orderId}'\0'${lineNumber}'\0'${view}`
    return this.sendMessage(KDS_CONTROLLER, KDS_CONTROLLER, TK_KDS_TOGGLE_TAG_LINE, FM_PARAM, 5000, data)
  }

  sendKDSToggleNamedTagLine(orderId, lineNumber, tagName, view) {
    const data = `${this.kdsId}\0${orderId}\0${lineNumber}\0${tagName}\0${view}`
    return this.sendMessage(KDS_CONTROLLER, KDS_CONTROLLER, TK_KDS_TOGGLE_TAG_LINE, FM_PARAM, 5000, data)
  }
}

export default MessageBus
