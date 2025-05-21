__gui_ajax_js__ = true;

/* message-bus commands */
var TK_KDS_GETMODEL =			"0xF0B00001";	/* retrieves the current model for a KDS (full model) */
var TK_KDS_UPDATEVIEW =			"0xF0B00002";	/* update view */
var TK_KDS_REFRESH =			"0xF0B00003";	/* refresh KDS orders */
var TK_KDS_SET_PROD_STATE =		"0xF0B00005";	/* set production state in a KDS order */
var TK_KDS_UNDO_SERVE =			"0xF0B00006";	/* undo last serve */
var TK_KDS_CHANGE_VIEW =		"0xF0B00007";	/* change KDS view dynamically */
var TK_KDS_TOGGLE_TAG_LINE =	"0xF0B00008";	/* toggle an order line tag state */
var TK_KDS_GLOBAL_SERVE =		"0xF0B00009";	/* serves the order in all monitors */
var TK_I18N_GETTABLEJSON =		"0x00700005";	/* retrieves the i18n table in JSON format */
var TK_EVT_EVENT =				"0xF0400001";	/* events manager */
var TK_SYS_ACK =				"0xF0100001";	/* ACK */
var TK_SYS_NAK =				"0xF0100002";	/* NAK */
var TK_HV_LOG =					 "0x0020000E";	/* hypervisor logger */

/* formats */
var FM_XML =			0x00000001;	/* xml file */
var FM_PARAM =			0x00000002;	/* parameters separated by '\0' character */
var FM_ADDR_PORT =		0x00000003;	/* 18 bytes, first 16 are the IPv6 address, last 2 are the port */
var FM_INT32 =			0x00000004;	/* 4 bytes representing a 32 bit integer */
var FM_INT64 =			0x00000005;	/* 8 bytes representing a 64 bit integer of two 32 bit integers */
var FM_STRING =			0x00000006;	/* a character array with an '\0' at the end */
var FM_STR_ARRAY_PIPE =	0x00000007;	/* an array of strings delimited by '|' pipe character ended with '\0' */

var EVENT_TIMEOUT = 10; /* event timeout in seconds */

/**
 * Sends a message to a service, using the HttpInterface as a "bridge"
 * @param service {string} - Name of the destination service
 * @param serviceType {string} - Type of the destination service
 * @param token {integer or hex string} - Token of the message being sent
 * @param format {integer or string} - Format of the message being sent. All integers are parsed by the server, as well as the strings "xml", "param" and "string"
 * @param timeout {integer or hex string} - Message timeout in microseconds (-1 for infinite)
 * @param data {string} - The message data
 * @param sendB64 {boolean} - if true, the message will be sent as base-64
 * @param callback {function} - Callback to receive a single parameter containing the AjaxResponse object for the message reply
 */
function sendMessage(service, serviceType, token, format, timeout, data, callback, sendB64) {
	var url = "/mwapp/services/"+serviceType+"/"+service+"?"+
		"token="+token+"&"+
		"format="+format+"&"+
		"timeout="+timeout+"&"+
		"isBase64="+(sendB64?"true":"false")+"&"+
		"_ts="+new Date().getTime();
	if (sendB64) data = encodeB64(data);
	new Ajax.Request(url, {
		method: 'post',
		postBody: data,
		onComplete: function(req) {
			_notifyConnStatus(req);
			callback(req); // call the real callback
		}
	});
}

/**
 * Sends a logging message to Hypervisor
 * @param level {String} - Log level (TRACE, DEBUG, INFO, WARN, ERROR, FATAL)
 * @param func {String} - Function name
 * @param msg {String} - Message to log
 */
function sendLogMessage(level, func, msg) {
	var data = (level+'\0'+"htdocs/kds/" + func+'\0'+msg);
	sendMessage("Hypervisor","Hypervisor",TK_HV_LOG,FM_PARAM,-1,data,Prototype.emptyFunction,true);
}


/**
 * Sends a message requesting the KDS model to KdsController
 * @param callback {function} - Callback to receive a single parameter containing the AjaxResponse object for the message reply
 */
function sendGetModelMessage(callback) {
	var data = String(_main.kdsId);
	sendMessage("KdsController","KdsController",TK_KDS_GETMODEL,FM_STRING,-1,data,callback);
}

/**
 * Sends a message to refresh KDS orders.
 * @param callback {function} - Callback to receive a single parameter containing the AjaxResponse object for the message reply
 */
function sendRefreshMessage() {
	var data = String(_main.kdsId);
	sendMessage("KdsController","KdsController",TK_KDS_REFRESH,FM_STRING,-1,data,
		function(req) {
			if(!_ajaxOk(req, true)) {
				/* On any failure, try again in 7.5 seconds*/
				_main.reload.delay(7.5);
			}
		},true);
}

/**
 * Sends a message to KDS controller informing new production state for an order.
 * @param orderId {integer} - Order to modify state
 * @param state {string} - New state
 */
function sendSetStateMessage(orderId, state) {
	var data = String(_main.kdsId)+'\0'+String(orderId)+'\0'+state;
	sendMessage("KdsController","KdsController",TK_KDS_SET_PROD_STATE,FM_PARAM,-1,data,Prototype.emptyFunction,true);
}

/**
 * Sends a message to KDS controller to undo last serve.
 */
function sendUndoServeMessage() {
	var data = String(_main.kdsId);
	sendMessage("KdsController","KdsController",TK_KDS_UNDO_SERVE,FM_STRING,-1,data,Prototype.emptyFunction,true);
}

/**
 * Sends a message to KDS controller to undo last serve.
 */
function sendGlobalServeMessage(orderId) {
	var data = String(_main.kdsId) + '\0' + String(orderId);
	sendMessage("KdsController","KdsController",TK_KDS_GLOBAL_SERVE,FM_PARAM,-1,data,Prototype.emptyFunction,true);
}

/**
 * Sends an event emulating a bump bar keypress.
 * @param name {string} - Bump bar id
 * @param code {integer} - Key code
 */
function sendBumpBarEvent(name, code) {
	var data = "" +
		'<Event subject="BUMP_BAR" type="KEY_PRESSED">\n' +
		'	<BumpBar name="' + String(name) + '" keycode="' + String(code) + '"/>\n' +
		'</Event>\n' +
		'\0BUMP_BAR\0KEY_PRESSED\0false\0'+_main.kdsId+'\0'+EVENT_TIMEOUT;
	sendMessage("Hypervisor","Hypervisor",TK_EVT_EVENT,FM_PARAM,-1,data,Prototype.emptyFunction,true);
}

/**
 * Sends a message to retrieve the I18N table for this KDS.
 * @param callback {function} - Callback to receive a single parameter containing the AjaxResponse object for the message reply
 */
function sendGetI18nMessage(callback) {
	var data = String(_main.language);
	sendMessage("I18N","I18N",TK_I18N_GETTABLEJSON,FM_STRING,-1,data,callback);
}

/**
 * Sends a message to KDS controller informing new view for this KDS.
 * @param newId {integer} - Replacemente KDS id view to switch to
 */
function sendChangeViewMessage(kdsId, callback) {
	var data = String(_main.kdsId)+'\0'+String(kdsId);
	sendMessage("KdsController","KdsController",TK_KDS_CHANGE_VIEW,FM_PARAM,-1,data,callback || Prototype.emptyFunction,true);
}

/**
 * Sends a message to KDS controller, to toggle current line tag state.
 */
function sendToggleTagLine(orderId, lineNumber) {
	// we need to go through KDS controller, because we don't know about queues here in the KDS, so we cannot talk directly to the production service
	var data = String(_main.kdsId)+'\0'+String(orderId)+'\0'+String(lineNumber);
	sendMessage("KdsController","KdsController",TK_KDS_TOGGLE_TAG_LINE,FM_PARAM,-1,data,Prototype.emptyFunction,true);
}

function _ajaxOk(res, checkToken) {
	try {
		var ok = res.request.success();
		if(ok) {
			ok = (parseInt(TK_SYS_NAK) != parseInt(res.getHeader("X-token")));
		}
		return ok;
	} catch(ex) {
		return false;
	}
}

function _notifyConnStatus(request, status) {
	try {
		var callback = _notifyConnStatus.conncallback;
		if (callback) {
			if (status) {
				callback(status);
			} else if (_ajaxOk(request)) {
				callback("ON");
			} else {
				callback("OFF");
			}
		}
	} catch (ex) {
		notifyException(ex);
	}
}

/**
 * Starts the events thread, to receive "server-side-push" events.
 * @param callback {function} - Callback to receive a DOM node with the events (when any event occur)
 * @param conncallback {function} - Callback to receive connection status changes ("ON" - connected, "OFF" - disconnected, "OUT_OF_SYNC" - out of sync)
 */
function startEventsThread(callback, conncallback, completecallback) { }

/** The events thread function  itself */
function _eventsThread() {
	var url = "/mwapp/events/listen?"+
	"subject=KDS"+_main.kdsId+"&"+
	"syncId="+_eventsThread.sync+"&"+
	"blocking="+(_eventsThread.lastFailed?"false":"true")+"&"+ /* to detect "reconnection" ASAP */
	"_ts="+new Date().getTime();
	new Ajax.Request(url, {
		method: 'get',
		onComplete: function(res) {
			try {
				if (res.getHeader("X-out-of-sync") == "true") {
					try {
						_notifyConnStatus(null,"OUT_OF_SYNC");
					} finally {
						_main.reload();
					}
					return;
				}
				_notifyConnStatus(res);
				if (_ajaxOk(res)) {
					_eventsThread.lastFailed = false;
					var sync = res.getHeader("X-sync-id");
					if (sync !== null) {
						_eventsThread.sync = sync;
							if (res.responseXML) _eventsThread.callback(res.responseXML.documentElement);
							/* success - keep the "thread" running */
							_eventsThread();
							return;
					}
				}
			} catch (ex) {
				notifyException(ex);
			}
			/* On any failure, try again in 7.5 seconds*/
			_eventsThread.lastFailed = true;
			_main.reload.delay(7.5);
		}
	});
}
