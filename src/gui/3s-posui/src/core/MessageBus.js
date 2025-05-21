import axios from 'axios'
import Base64 from 'base64-js'
import utf8 from 'utf8'

const TK_POS_GETMODEL = '0xF0500001' /* retrieves the current model for a POS (full model) */
const TK_POS_EXECUTEACTION = '0xF0500003' /* executes an action */
const TK_POS_DIALOGRESP = '0xF0500007' /* response for a dialog box */
const TK_POS_ASYNCACTION = '0xF0500014' /* executes an action asyncronously */


const TK_I18N_GETTABLEJSON = '0x00700005' /* retrieves the i18n table in JSON format */


/* formats */
const FM_PARAM = 0x00000002 /* parameters separated by '\0' character */
const FM_STRING = 0x00000006 /* a character array with an '\0' at the end */


class MessageBus {
  constructor(posId = 0) {
    this.posId = posId
    this.posService = `POS${parseInt(this.posId, 10)}`
  }

  /**
   * Sends a message to a service, using the HttpInterface as a "bridge"
   * @param service {string} - Name of the destination service
   * @param serviceType {string} - Type of the destination service
   * @param token {integer or hex string} - Token of the message being sent
   * @param format {integer or string} - Format of the message being sent. All integers are
   *        parsed by the server, as well as the strings "xml", "param" and "string"
   * @param timeout {integer or hex string} - Message timeout in microseconds (-1 for infinite)
   * @param data {string} - The message data
   * @param sendB64 {boolean} - if true, the message will be sent as base-64
   */
  sendMessage = (service, serviceType, token, format = FM_STRING, timeout = -1, data = '', sendB64 = false) => {
    const timeStamp = (new Date()).getTime()
    const isFirefox = typeof InstallTrigger !== 'undefined'
    let isBase64 = sendB64
    if (!isBase64 && data.indexOf('\0') !== -1 && isFirefox) {
      isBase64 = true /* Firefox bug workaround */
    }
    const isBase64Str = (isBase64) ? 'true' : 'false'
    // eslint-disable-next-line max-len
    const url = `/mwapp/services/${serviceType}/${service}?token=${token}&format=${format}&timeout=${timeout}&isBase64=${isBase64Str}&_ts=${timeStamp}`
    let data64 = null
    if (isBase64) {
      const byteArray = []
      const len = data.length
      for (let i = 0; i < len; i++) {
        byteArray.push(data.charCodeAt(i) & 0xFF) // eslint-disable-line
      }
      data64 = Base64.fromByteArray(byteArray)
    }
    return axios.post(url, (isBase64) ? data64 : data)
      .then(response => {
        // get the synchronization id that will be necessary to listen to events
        return { 'ok': true, 'data': response.data }
      }, () => {
        console.error(`Axios Exception... URL: (${url})`)
        return { 'ok': false }
      })
  }

  /**
   * Sends a message requesting the POS model to POS controller
   */
  getPosModel() {
    return this.sendMessage(this.posService, 'POS', TK_POS_GETMODEL, FM_STRING, -1, String(this.posId))
  }

  encodeParam = (param) => {
    let encodedParam = param

    try {
      if (typeof param === 'string' || param instanceof String) {
        encodedParam = utf8.encode(`${param}`)
      }
    } catch (err) {
      // if a non-scalar value was provided, just send it without UTF-8 conversion
    }
    return encodedParam
  }

  encodeParams(params) {
    const encodedParams = []

    for (let i = 0; i < (params || []).length; i++) {
      encodedParams.push(this.encodeParam(params[i]))
    }
    return encodedParams
  }

  /**
   * Sends a message requesting an action execution.
   * @param actionName {String} - Action name
   * @param params {Array} - Action parameters
   */
  action(actionName, ...params) {
    return this.sendMessage(this.posService, 'POS', TK_POS_ASYNCACTION, FM_PARAM, -1, [actionName, this.posId, ...this.encodeParams(params)].join('\0'), true)
  }

  /**
   * Sends a message requesting an action execution (synchronous version).
   * @param actionName {String} - Action name
   * @param params {Array} - Action parameters
   */
  syncAction(actionName, ...params) {
    return this.sendMessage(this.posService, 'POS', TK_POS_EXECUTEACTION, FM_PARAM, -1, [actionName, this.posId, ...this.encodeParams(params)].join('\0'), true)
  }

  /**
   * Sends a message with a dialog response to Pos Controller.
   * @param dialogId {String} - Dialog id
   * @param response {String} - Dialog response
   */
  sendDialogResponseMessage(dialogId, response) {
    return this.sendMessage(this.posService, 'POS', TK_POS_DIALOGRESP, FM_PARAM, -1, [this.posId, dialogId, this.encodeParam(response)].join('\0'), true)
  }

  /**
   * Sends a message to retrieve the I18N table for this POS.
   * @param lang {function} - Language code to load
   */
  sendGetI18nMessage(lang) {
    return this.sendMessage('I18N', 'I18N', TK_I18N_GETTABLEJSON, FM_STRING, -1, lang)
  }
}

export default MessageBus
