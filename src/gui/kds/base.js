/*!
 * Base javascript functions.
 * As a general rule, this should only contain generic javascript
 * code, that is not specific related to application itself.
 * 
 * Please note that this depends on the "prototype.js" library.
 * 
 * Copyright © 2008-2009 MWneo Corporation
 * 
 * $Source:  $
 * $Revision$
 * $Date$ (of revision)
 * $Author$ (of revision)
 */

__base_js__ = true;
 
/**
 * Overrides the default behavior of the Request#success() method.
 * This ensures the same behavior under Firefox and IE.
 * As a result of this, a connection error will be sent to
 * the "onException" callback, instead of "onFailure".
 */
Ajax.Request.prototype.success = function() {
	if (this.transport.status == 12029 || this.transport.status == 503) {
		throw "CONN ERROR (" + this.transport.status + ")"; // Connection error on IE
	}
	// On Firefox, calling "this.transport.status" sometimes results in an error
	if (!this.transport.status) {
		throw "CONN ERROR";
	}
	return (this.transport.status >= 200 && this.transport.status < 300);
}
/**
 * Defines a new "Event.observe_many()" function that acts exactly
 * as "Event.observe()" but accepts an array of elements (instead
 * of just one).
 */
Event.observe_many = function(array, name, observer, useCapture) {
	$A(array).each(function(element) {
		Event.observe(element, name, observer, useCapture);
	});
}
/**
 * Defines a new "Element.toggle_many" function that acts exactly
 * as "Element.toggle()" but accepts an array of elements (instead
 * of just one).
 */
Element.toggle_many = function(array) {
	$A(array).each(function(element) {
		Element.toggle(element);
	});
}

/**
 * Adds an option to a <select> object.
 * This function was created because MSIE has a BUG which does not allow us to use innerHTML
 * to add options. (http://support.microsoft.com/?scid=kb%3Ben-us%3B276228&x=10&y=9)
 * @param element "<select>" element or id.
 * @param text option text
 * @param value option value (defaults to text parameter)
 * @param selected (true|false)
 */
function addSelectOption(element, text, value, selected) {
	var option = document.createElement('option');
	option.text = text;
	option.value = value || text;
	element = $(element);
	try {
		roles_select.add(option, null); // standards compliant
	} catch(ex) {
		roles_select.add(option); // IE only
	}
	option.selected = selected;
}
/**
 * Gets the name and values (optional) of an object's properties.
 * @param obj object to get properties
 * @param includeValues if true, the values will be included in the result
 * @return string
 */
function getProps(obj, includeValues) {
	var str = "";
	for (var prop in obj) {
		str += prop;
		if (includeValues) {
			str += " = " + obj[prop];
		}
		str += "\n";
	}
	return str;
}

/**
 * Attempts to focus an element, and catchs any exception raised.
 * @param element dom node or id
 */
function tryFocus(element) {
	try {$(element).focus();} catch(ex){}
}
/**
 * Attempts to select an element's content, and catchs any exception raised.
 * @param element dom node or id
 */
function trySelect(element) {
	try {$(element).select();} catch(ex){}
}
/** Parses an XML text and returns the DOM node */
function parseXmlText(text) {
	var xmlDoc = null;
	if (window.ActiveXObject) {
		xmlDoc = new ActiveXObject("Microsoft.XMLDOM");
		xmlDoc.async = false;
		xmlDoc.loadXML(text);
	} else if (document.implementation && document.implementation.createDocument) {
		var parser = new DOMParser();
		xmlDoc = parser.parseFromString(text, "text/xml");
	} else {
		fatalError("This browser does not support xml-text parsing");
	}
	return xmlDoc;
}
if (!this.atob || !this.btoa) {
	var B64_keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
	var base64test = /[^A-Za-z0-9\+\/\=]/g;
}
/** Encodes a text to BASE64 */
function encodeB64(input) {
	if (this.btoa) {
		// Mozilla / opera has native base 64 encoder
		return btoa(input);
	}
	var output = "";
	var chr1, chr2, chr3 = "";
	var enc1, enc2, enc3, enc4 = "";
	var i = 0;

	do {
		chr1 = input.charCodeAt(i++);
		chr2 = input.charCodeAt(i++);
		chr3 = input.charCodeAt(i++);

		enc1 = chr1 >> 2;
		enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
		enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
		enc4 = chr3 & 63;

		if (isNaN(chr2)) {
			enc3 = enc4 = 64;
		} else if (isNaN(chr3)) {
			enc4 = 64;
		}
		output = output + 
			B64_keyStr.charAt(enc1) + 
			B64_keyStr.charAt(enc2) + 
			B64_keyStr.charAt(enc3) + 
			B64_keyStr.charAt(enc4);
		chr1 = chr2 = chr3 = "";
	} while (i < input.length);
	return output;
}
/** Decodes a BASE64 to plain text */
function decodeB64(input) {
	if (this.atob) {
		// Mozilla / opera has native base 64 decoder
		return atob(input);
	}
	var output = "";
	var chr1, chr2, chr3 = "";
	var enc1, enc2, enc3, enc4 = "";
	var i = 0;
	/* The commented lines bellow should be used to clean '\n', etc... if needed
	if (base64test.exec(input)) {
		throw new Error("There were invalid base64 characters in the input text");
	}
	// remove all characters that are not A-Z, a-z, 0-9, +, /, or =
	input = input.replace(/[^A-Za-z0-9\+\/\=]/g, "");
	*/
	do {
		enc1 = B64_keyStr.indexOf(input.charAt(i++));
		enc2 = B64_keyStr.indexOf(input.charAt(i++));
		enc3 = B64_keyStr.indexOf(input.charAt(i++));
		enc4 = B64_keyStr.indexOf(input.charAt(i++));

		chr1 = (enc1 << 2) | (enc2 >> 4);
		chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);
		chr3 = ((enc3 & 3) << 6) | enc4;

		output = output + String.fromCharCode(chr1);
		if (enc3 != 64) output = output + String.fromCharCode(chr2);
		if (enc4 != 64) output = output + String.fromCharCode(chr3);

		enc1 = enc2 = enc3 = enc4 = "";
	} while (i < input.length);
	return output;
}
/** Gets the text data from the given node */
function getTextData(node) {
	var text = "";
	node = node.firstChild;
	while (node) {
		if (isTextNode(node)) {
			text += node.data;
		}
		node = node.nextSibling;
	}
	return text;
}
/** Checks if a DOM node represents a text node */
function isTextNode(node) {
	return node && (node.nodeType == 3);
}
/** Returns the first element of the given node list */
function firstElement(nodeList) {
	for (var i = 0; i < nodeList.length; i++) {
		if (isElement(nodeList[i])) {
			return nodeList[i];
		}
	}
	return null;
}
/** Returns the first child element of the given node */
function firstChildElement(node) {
	return firstElement(node.childNodes);
}
/** Returns the next element from the given node */
function nextElement(node) {
	do {
		node = node.nextSibling;
	} while (node && !isElement(node));
	return node;
}
function isDOM(o)       { return isObject(o) && o.getElementsByTagName}
function isAlien(a)     { return isObject(a) && typeof a.constructor != 'function' }
function isArray(a)     { return isObject(a) && a.constructor == Array }
function isError(a)     { return a instanceof Error }
function isBoolean(a)   { return typeof a == 'boolean' }
function isFunction(a)  { return typeof a == 'function' }
function isNull(a)      { return typeof a == 'object' && !a }
function isNumber(a)    { return typeof a == 'number' && isFinite(a) }
function isInteger(a)   { return isNumber(a) && parseInt(a) == a}
function isObject(a)    { return (a && typeof a == 'object') || isFunction(a) }
function isRegexp(a)    { return a && a.constructor == RegExp }
function isString(a)    { return typeof a == 'string' }
function isUndefined(a) { return typeof a == 'undefined' }
function undef(v)       { return  isUndefined(v) }
function isdef(v)       { return !isUndefined(v) }
function isList(o)      { return o && isObject(o) && (isArray(o) || o.item) }
function isElement(o, strict) { return o && isObject(o) && ((!strict && (o==window || o==document)) || o.nodeType == 1) }

/** Pad a number with 0 on the left */
function padDigits(n, totalDigits) {
	n = n.toString();
	var pd = '';
	var len = n.length;
	if(totalDigits > len) {
		for(let i = 0; i < (totalDigits - len); i++) {
			pd += '0';
		}
	}
	return(pd + n);
}

/** Extends Date to accept ISO8601 format */
Date.prototype.setISO8601 = function(string, gmt) {
	var regexp = "([0-9]{4})(-([0-9]{2})(-([0-9]{2})" +
				 "(T([0-9]{2}):([0-9]{2})(:([0-9]{2})(\.([0-9]+))?)?" +
				 "(Z|(([-+])([0-9]{2}):([0-9]{2})))?)?)?)?";
	var d = string.match(new RegExp(regexp));
	var offset = 0;
	var date = new Date(d[1], 0, 1);
	if(d[3]) { date.setMonth(d[3] - 1); }
	if(d[5]) { date.setDate(d[5]); }
	if(d[7]) { date.setHours(d[7]); }
	if(d[8]) { date.setMinutes(d[8]); }
	if(d[10]) { date.setSeconds(d[10]); }
	if(d[12]) { date.setMilliseconds(Number("0." + d[12]) * 1000); }
	if(d[14]) {
	    offset = (Number(d[16]) * 60) + Number(d[17]);
	    offset *= ((d[15] == '-') ? 1 : -1);
	}
	if (gmt) offset -= date.getTimezoneOffset();
	time = (Number(date) + (offset * 60 * 1000));
	this.setTime(Number(time));
}
