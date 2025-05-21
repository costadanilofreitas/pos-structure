/*!
 * KDS GUI main procedures
 *
 * Copyright (C) 2008-2011 MWneo Corporation
 *
 * $Revision$
 * $Date$ (of revision)
 * $Author$ (of revision)
 */

var _main = {
	kdsId: -1,					/* our KDS id */
	model: new Hash(),			/* model variables */
	modelTagHooks: new Hash(),	/* hooks (when event is received) */
	cells: [],					/* sale cells */
	cellIndex: 0,				/* first visible cell (show cells in blocks of visible cells) */
	screenCellLimit: 0,			/* maximum number of cells in the screen*/
	freeCells: [],				/* free sale cells that can be reused */
	keepFocus: false,			/* to know when the refresh is finished */
	focus: 0,					/* index of the focused cell */
	visibleCells: 0,			/* number of visible cells updated in sortCells */
	cellPadding: 5,				/* padding inside cell body */
	clockId: 0,					/* time clock id */
	language: "en",				/* language */
	thresholds: new Hash(),		/* list of thresholds */
	orderImages: new Hash(),	/* cached order images */
	i18nTable: {},				/* i18n table */
	statusBar: null,			/* status bar <div> */
	title: "",					/* optional KDS title */
	effects: "on",				/* effects state (on/off) -- low not implemented */
	holdDroppable: null,		/* <div> to drop */
	bodyDiv: null,				/* main container <div> that holds other objects in the screen */
	heldDelayTimeout: null,		/* held zone delay id */
	zoomBumpBarName: "",		/* bump bar name used to emulate a zoom command */
	zoomBumpBarCode: 0,			/* bump bar zoom command code */
	cellHeaderFmt: "",			/* cell header format string */
	cellFooterFmt: "",			/* cell footer format string */
	simulateBumpBar: false,		/* indicates if we should simulate bump-bar events */
	simulateBumpBarName: null,	/* name of the bumpbar to simulate */
	forcedRefreshTimeout: null,	/* timeout to force a startup refresh */
	simulateBuzzer: false,		/* indicates if we should simulate buzzer sounds */
	soundFile: "alert1.wav",	/* alert sound file for simulated buzzer */
	showCellItems: true,		/* whether items must be displayed */
	selectableIds: [],			/* list of selectable KDS ids */
	replacementId: null,		/* current replcement id */
	kdsTitles: {},				/* KDS titles indexed by KDS id */
	switchKdsCont: null,		/* switch KDS container <div> */
	switchKdsTimeout: null,		/* switch timeout for closing the dialog automatically */
	switchKdsCurrent: null,		/* current KDS selected for switch */
	headerLines: 1,				/* number of lines reserved for header */
	footerLines: 1,				/* number of lines reserved for footer */
	headerColumns: -1,			/* number of columns in which the header must be displayed (-1 means all = default) */
	enableTagging: false,		// Enable item / mod tagging
	showVoidOrders: false,		/* Whether to display voided orders in the KDS*/
	showWarningScreen: false,	/* Whether to display connection error on the main screen */

	/**
	 * Callback that is called everytime some events arrive from the server.
	 * @param root {DOM} - Events document root
	 */
	receiveEvents: function(root) {
		if(!root) return;
		var refreshEndEvent = null;
		var event = firstChildElement(root);
		while(event) {
			var node = firstChildElement(event);
			while(node) {
				var name = node.nodeName;
				if(name == "RefreshEnd") {
					/* keep this one for the end, to avoid focus issue when the page is loaded for the first time */
					refreshEndEvent = node;
					/* clear forced refresh timeout */
					if(_main.forcedRefreshTimeout) {
						clearTimeout(_main.forcedRefreshTimeout);
						_main.forcedRefreshTimeout = null;
					}
				} else {
					_main.modelChanged(node);
				}
				node = nextElement(node);
			}
			event = nextElement(event);
		}
		/* this will allow sortCells to run */
		if(refreshEndEvent) {
			_main.modelChanged(refreshEndEvent);
		}
	},
	/**
	 * Callback that is called everytime a connection status change is detected.
	 * @param status {string} - "ON" - connected, "OFF" - disconnected, "OUT_OF_SYNC" - out of sync
	 */
	receiveConnStatus: function(status) {
		if (status == "OUT_OF_SYNC") {
			// TODO - display some visual information that the GUI will be reloaded
			console.log("KDS UI is out of sync");
		} else if (status != _main.model.get("SERVER_CONNECTION")) {
			_main.model.set("SERVER_CONNECTION", status);
			if(status == "ON") {
				$('warning_screen').hide();
				$('main_body_div').show();
				$('status_bar_conn_off').hide();
				$('status_bar_conn_on').show();
			} else {
				$('status_bar_conn_on').hide();
				$('status_bar_conn_off').show();
				if (_main.showWarningScreen === true) {
					$('main_body_div').hide();
					$('warning_screen').show();
				}
				console.log("Error connecting to KDS Controller status=" + status + " stack:\n" + Error().stack);
			}
		}
	},
	/**
	 * Loads a full KDS model.
	 * @param domNode {DOM} - KdsModel document root
	 */
	loadModel: function(domNode) {
		var node = firstChildElement(domNode);
		while (node) {
			_main.modelChanged(node);
			node = nextElement(node);
		}
	},
	/**
	 * Function shared by "receiveEvents" and "loadModel" to indicate that a single model node has changed.
	 * This function will delegate the responsability for the registered function for that tag. (See "bindModelTagHooks").
	 * @param modelNode {DOM} - Node with the model modification
	 */
	modelChanged: function(modelNode)  {
		var name = modelNode.nodeName;
		var hook = _main.modelTagHooks.get(name);
		if (hook) {
			try { hook(modelNode); } catch (ex) { notifyException(ex); }
		}
	},
	/**
	 * Force a refresh when "RefreshEnd" events does not comes after N seconds
	 */
	forcedRefresh: function() {
		var hook = _main.modelTagHooks.get("RefreshEnd");
		if (hook) {
			try { hook(null); } catch (ex) { notifyException(ex); }
		}
		_main.forcedRefreshTimeout = null;
	},
	/**
	 * Initialize model with default values
	 */
	initModel: function() {
		_main.model = new Hash({
			"COLS": 8,
			"ROWS": 2,
			"HOLD": -1,
			"TOTAL": -1,
			"LINES": 19,
			"FONTSIZE": -1,
			"IMAGELINES": 0,
			"SERVER_CONNECTION": "ON"
		});
	},
	/**
	 * Bind hooks to handle model changes.
	 */
	bindModelTagHooks: function() { },
	/**
	 * Starts simulating bumpbar events
	 */
	startSimulateBumpbar: function() { },
	/**
	 * Ensure valid focus
	 * @param defaultHome {boolean} - When true focus goes to the first cell, else loops to first/last cell on overflow/underflow
	 */
	adjustFocus: function(defaultHome) {
		if(defaultHome) {
			if((_main.focus >= _main.visibleCells) || (_main.focus < 0)) {
				_main.focus = 0;
			}
			return;
		}
		var totalCells = _main.cells.length;
		if(_main.focus >= _main.visibleCells) {
			var globalIndex = _main.focus + _main.cellIndex;
			//scrolling forward
			if (globalIndex <= totalCells) {
				//we can scroll to the next orders
				if (_main.cells[globalIndex - 1].hasMoreItems()) {
					//last order did not have enough space, will be displayed with all cells in the next page
					_main.cellIndex += _main.visibleCells -1;
				} else if (globalIndex <  totalCells){
					//there are more orders, not just more cells from a clipped order
					_main.cellIndex += _main.visibleCells;
				} else {
					//no more orders
					_main.cellIndex = 0;
				}
			} else {
				//no more orders, back to the beginning
				_main.cellIndex = 0;
			}
			_main.sortCells();
			_main.focus = 0;
		} else if(_main.focus < 0) {
			//scrolling backward
			if (_main.cellIndex > 0) {
				//we can scroll to the previous orders
				_main.cellIndex = _main.getPreviousIndex();
			} else {
				//we are at the beginning, go to the last orders
				_main.cellIndex = _main.getLastIndex();
			}
			_main.sortCells();
			_main.focus = (_main.visibleCells - 1);
		}
		if(_main.focus < 0) {
			_main.focus = 0;
		}
	},
	getPreviousIndex: function() {
		var cells = 0;
		for (var index = _main.cellIndex - 1; index >= 0; index--) {
			var cell = _main.cells[index];
			cells += cell.getCellSize();
			if (cells >= _main.screenCellLimit) {
				return index;
			}
		}
		return 0;
	},
	getLastIndex: function() {
		var cells = 0;
		var cellIndex = 0;
		for (var index = 0; index < _main.cells.length; index++) {
			var cell = _main.cells[index];
			cells += cell.getCellSize();
			if (cells > _main.screenCellLimit) {
				cellIndex = index;
				cells = cells - _main.screenCellLimit;
			}
		}
		return cellIndex;
	},
	/**
	 * Focus mouse selected cell
	 */
	onCellClick: function(cell) {
		_main.tryToSetFocus(cell);
		_main.refreshFocus();
	},
	/**
	 * Bump mouse double-clicked cell
	 */
	onCellDoubleClick: function(cell) {
		sendSetStateMessage(cell.getOrderId(), "SERVED");
	},
	/**
	 * Called when a drag cell starts
	 */
	onStartDrag: function(cell) {
		if(_main.holdDroppable) {
			_main.heldDelayTimeout = _main.holdDroppable.show.bind(_main.holdDroppable).delay(0.5);
		}
	},
	/**
	 * Called when a cell is released in a droppable element
	 */
	onEndDrag: function(cell) {
		if(_main.holdDroppable) {
			if(_main.heldDelayTimeout) {
				clearTimeout(_main.heldDelayTimeout);
				_main.heldDelayTimeout = null;
			}
			_main.holdDroppable.hide();
		}
	},
	/**
	 * Called when a cell is released in a non-droppable element
	 */
	onRevertDrag: function(cell) {
		_main.sortCells();
	},
	parseQuery: function(qstr) {
		var query = {};
		var a = qstr.substr(1).split('&');
		for (var i = 0; i < a.length; i++) {
			var b = a[i].split('=');
			query[decodeURIComponent(b[0])] = decodeURIComponent(b[1] || '');
		}
		return query;
	},
	/**
	 * Loads the KDS GUI
	 */
	load: function() {
		var qs = _main.parseQuery(window.location.search);
		/* find our "kdsid" on the query string */
		if (!qs.kdsid) {
			alert("Please, specify a valid 'kdsid' in the URL");
			return;
		}
		/* call initialization functions */
		_main.kdsId = qs.kdsid;
		_main.forcedRefreshTimeout = setTimeout(_main.forcedRefresh, 7000);
		_main.model.set("SERVER_CONNECTION", "ON");
		_main.bindModelTagHooks();
		_main.createMainBodyDiv();
		_main.createWarningScreen();
		_main.createHoldDroppable();
		_main.createStatusBar();
		startEventsThread.curry(_main.receiveEvents, _main.receiveConnStatus, _main.onCompleteLoad).defer();
		/* begin timeout to update order's header */
		_main.clockId = setTimeout(_main.updateClock, 100);
		/* observe window resizes */
		Event.observe(window, 'resize', _main.onResize);
		document.title = "KDS " + _main.kdsId;
		if (typeof(custom) !== "undefined" && custom !== null && custom.init !== undefined) {
			custom.init();
		}
	},
	/**
	 * Called when the window is resized
	 */
	onResize: function() {
		if (_main.onResize.timeout) {
			clearTimeout(_main.onResize.timeout);
			_main.onResize.timeout = 0;
		}
		_main.onResize.timeout = setTimeout(_main.reload, 2000);
	},
	/**
	 * Called when the server events are successfully binded
	 */
	onCompleteLoad: function() {
		/* get the current model for this KDS from the KDS Controller */
		sendGetModelMessage(function(req) {
			try {
				if (req.responseXML) {
					var modelDom = req.responseXML.documentElement;
					_main.loadModel(modelDom);
					/* refresh KDS orders */
					sendRefreshMessage();
					return;
				}
			} catch(ex) {
				notifyException(ex);
			}
			/* On any failure, try again in 7.5 seconds*/
			_main.reload.delay(7.5);
		});
	},
	/**
	 * Connection icon double-click
	 */
	onConnDoubleClick: function(element) {
		_main.reload();
	},
	/**
	 * Zoom icon click
	 */
	onZoomClick: function(element) {
		sendBumpBarEvent(_main.zoomBumpBarName, _main.zoomBumpBarCode);
	},
	/**
	 * Recall icon click
	 */
	onRecallClick: function(element) {
		sendUndoServeMessage();
	},
	/**
	 * Set main body <div> size
	 * @param viewport {object} - Must contain properties "width" and "height" with the client viewport dimensions in pixels
	 */
	setMainBodySize: function(viewport) {
		_main.setDivSize(_main.bodyDiv, viewport);
	},
	/**
	 * Set a <div> size
	 * @param viewport {object} - Must contain properties "width" and "height" with the client viewport dimensions in pixels
	 */
	setDivSize: function(div, viewport) {
		div.style.top = "0px";
		div.style.left = "0px";
		div.style.width = viewport.width + "px";
		div.style.height = viewport.height + "px";
	},
	/**
	 * Creates the main body <div> that will contain the cells
	 */
	createMainBodyDiv: function() {
		var viewport = { width: 0, height: 0 };
		_main.getViewportSize(viewport);
		var mainbody = document.getElementsByTagName('body')[0];
		var frag = document.createDocumentFragment();
		var obj = document.createElement('div');
		var id = "main_body_div";
		frag.appendChild(obj);
		mainbody.insertBefore(frag, mainbody.firstChild);
		obj.setAttribute('id', id);
		_main.bodyDiv = $(id);
		Element.addClassName(_main.bodyDiv, 'mainBodyDiv');
		_main.setMainBodySize(viewport);
		disableTextSelection(_main.bodyDiv);
	},
	createWarningScreen: function() {
		var div = document.createElement('div');
		div.setAttribute('id', 'warning_screen');
		Element.addClassName(div, 'warningScreen');
		var viewport = { width: 0, height: 0 };
		_main.getViewportSize(viewport);
		_main.setDivSize(div, viewport);
		div.innerHTML = '<i class=\"fa fa-5x fa-exclamation-triangle\" aria-hidden=\"true\"></i>';
		div.hide();
		var mainbody = document.getElementsByTagName('body')[0];
		var frag = document.createDocumentFragment();
		frag.appendChild(div);
		mainbody.insertBefore(frag, mainbody.firstChild);
	},
	/**
	 * Creates hold droppable <div> (inside main body <div>)
	 */
	createHoldDroppable: function() {
		var id = "hold_droppable";
		if($(id)) {
			return;
		}
		var mainbody = _main.bodyDiv;
		var frag = document.createDocumentFragment();
		var obj = document.createElement('div');
		obj.style.display = 'none';
		frag.appendChild(obj);
		mainbody.insertBefore(frag, mainbody.firstChild);
		obj.setAttribute('id', id);
		_main.holdDroppable = $(id);
		_main.updateHoldDroppableText();
		new Effect.Opacity(_main.holdDroppable, { from: 1.0, to: 0.5, duration: 0 });
		Element.addClassName(_main.holdDroppable, 'holdDroppable');
		Droppables.add(_main.holdDroppable, {
			onDrop: function(element) {
				var cell = _main.getFocusedCell();
				if(cell) {
					sendSetStateMessage(cell.getOrderId(), (cell.getProductionState() == "HELD") ? "NORMAL" : "HELD");
				}
  			}
		});
		disableTextSelection(_main.holdDroppable);
	},
	/**
	 * Helper function to update the hold droppable text "Drop the order here..."
	 */
	updateHoldDroppableText: function() {
		var html = '<div class="holdDroppableMessage">' + I18N("$DROP_ORDER_HERE_HELD") + "</div>";
		_main.holdDroppable.update(html);
	},
	/**
	 * Creates the main status bar <div>, note that is outside of the main body <div>
	 */
	createStatusBar: function() {
		var mainbody = document.getElementsByTagName('body')[0];
		var frag = document.createDocumentFragment();
		var obj = document.createElement('div');
		var id = "status_bar_cont";
		obj.style.display = 'none';
		frag.appendChild(obj);
		mainbody.insertBefore(frag, mainbody.firstChild);
		obj.setAttribute('id', id);
		_main.statusBar = $(id);
		Element.addClassName(_main.statusBar, 'statusBar');
		var html = "<table id=\"status_bar_table\" class=\"statusBarTable\"><tr>";
		html += "<td class=\"statusBarZoomIcon\"><div id=\"status_bar_zoom_icon\" class=\"statusBarZoomIcon\"><i class=\"statusBarIcon fa fa-search\" aria-hidden=\"true\"></i></div></td>";
		html += "<td class=\"statusBarText\"><div id=\"status_bar_text\"></div></td>";
		html += "<td><div id=\"status_bar_recall_icon\" class=\"statusBarRecallIcon\"><i class=\"statusBarIcon fa fa-undo\" aria-hidden=\"true\"></i></div></td>";
		html += "<td class=\"statusBarConnIcon\"><div id=\"status_bar_conn_icon\" class=\"statusBarConnIconCont\"><div id=\"status_bar_conn_on\" class=\"statusBarConnIcon statusBarConnIconOn\"><i class=\"statusBarIcon fa fa-wifi\" aria-hidden=\"true\"></i></div><div id=\"status_bar_conn_off\" class=\"statusBarConnIcon statusBarConnIconOff\" style=\"display: none;\"><i class=\"statusBarIcon fa fa-exclamation-triangle\" aria-hidden=\"true\"></i></div></div></td>";
		html += "</tr></table>";
		_main.statusBar.update(html);
		$('status_bar_conn_icon').observe('dblclick', _main.onConnDoubleClick.bindAsEventListener(_main));
		$('status_bar_zoom_icon').observe('click', _main.onZoomClick.bindAsEventListener(_main));
		$('status_bar_recall_icon').observe('click', _main.onRecallClick.bindAsEventListener(_main));
		_main.statusBarText = $("status_bar_text");
		_main.statusBar.show();
		disableTextSelection(_main.statusBar);
	},
	/**
	 * The timeout function that refreshes order's header
	 */
	updateClock: function() { },
	/**
	 * Clear order's header refresh timeout
	 */
	killClock: function() {
		if(_main.clockId) {
			clearTimeout(_main.clockId);
			_main.clockId = null;
		}
	},
	/**
	 * Sort cells by display order (coming from production subsystem)
	 */
	sortByDisplayOrder: function(cell1, cell2) {
		var a = cell1.getDisplayOrder();
		var b = cell2.getDisplayOrder();
		if (a<b) return -1;
		if (a>b) return 1;
		return 0;
	},
	/**
	 * Calculate visible area to display cells, substracting the status bar zone
	 * @param size {object} - Must contain properties "width" and "height" to store the client viewport dimensions in pixels
	 */
	getViewportSize: function(size) {
		if(typeof window.innerWidth != 'undefined') {
			/* the more standards compliant browsers (mozilla/netscape/opera/IE7) use window.innerWidth and window.innerHeight */
			size.width = window.innerWidth;
			size.height = window.innerHeight;
		} else if((typeof document.documentElement != 'undefined') &&
				  (typeof document.documentElement.clientWidth != 'undefined') &&
				  (document.documentElement.clientWidth !== 0)) {
			/* IE6 in standards compliant mode (i.e. with a valid doctype as the first line in the document) */
			size.width = document.documentElement.clientWidth;
			size.height = document.documentElement.clientHeight;
		} else {
			/* older versions of IE */
			size.width = document.getElementsByTagName('body')[0].clientWidth;
			size.height = document.getElementsByTagName('body')[0].clientHeight;
		}
		if(_main.statusBar) {
			if(_main.statusBar.offsetHeight) {
			     size.height -= _main.statusBar.offsetHeight;
			} else if(_main.statusBar.pixelHeight) {
			     size.height -= _main.statusBar.pixelHeight;
			}
		}
	},
	/**
	 * Loop through visible cells refreshing focus style
	 */
	refreshFocus: function() {
		var visibleIdx = 0;
		_main.cells.each(function(cell) {
			if(cell.isVisible()) {
				cell.setFocus(_main.focus == visibleIdx);
				visibleIdx++;
			}
		});
	},
	/**
	 * Get visible cell at given index
	 * @param idx {integer} - The index of the visible cell to retrieve
	 */
	getVisibleCell: function(idx) {
		var cellRet = null;
		var visibleIdx = 0;
		_main.cells.each(function(cell) {
			if(cell.isVisible()) {
				if(idx == visibleIdx) {
					cellRet = cell;
					throw $break;
				}
				visibleIdx++;
			}
		});
		return(cellRet);
	},
	/**
	 * Get currently focused cell
	 */
	getFocusedCell: function() {
		return(_main.getVisibleCell(_main.focus));
	},
	/**
	 * Tries to set the focus on the given cell (if valid)
	 * @param cellToFocus {object} - The Cell.Sale cell to focus.
	 */
	tryToSetFocus: function(cellToFocus) {
		if(cellToFocus !== null) {
			var visibleIdx = 0;
			var found = false;
			_main.cells.each(function(cell) {
				if(cell.getOrderId() == cellToFocus.getOrderId()) {
					if(cell.isVisible()) {
						found = true;
						_main.focus = visibleIdx;
					}
					throw $break;
				}
				if(cell.isVisible()) {
					visibleIdx++;
				}
			});
			/* order was probably bumped */
			if(!found) {
				_main.focus = 0;
			}
		}
	},
	/**
	 * This is the main function that sorts cells on screen, taking in account held cells.
	 * Note that it traverses all the columns and rows configured for current zoom level
	 * storing the calculated position of order cells, cells continuations and cell body columns
	 * in an array called "rearrange". Then the elements are rearranged based on the calculated
	 * positions.
	 * An order consist of a main Cell.Sale with N "body columns" that always can be limited
	 * by Cell.Sale.maxColSpan property. If a cell expands to the next row, then a new Cell.Sale
	 * (referred as "continuation cell" in this script) is created by Cell.Sale.getCellByRow and
	 * added to the Cell.Sale._contdCell of the main cell.
	 * A body column related to an order may change the parent cell, for example if the zoom is
	 * changed the second column of an order may need to be moved to a continuation cell.
	 * In general, continuation cells are not destroyed when the zoom changes, but hidden to be
	 * reused later if necessary.
	 */
	sortCells: function() { },
	playSound: function(file) {
		var obj = $('alert_sound');
		if(obj) {
			obj.remove();
		}
		var url = 'sounds/' + file;
		var node = new Element('object', { 'id': 'alert_sound', 'type': 'audio/x-wav', 'data': url, 'width': '1', 'height': '1',  'style': 'bottom: 0; left: 0px; position: absolute;' });
		var html =	'<param name="src" value="' + url + '">' +
					'<param name="autoplay" value="true">' +
					'<param name="autoStart" value="1">' +
					'alt : <a href="' + url + '">wav</a>';
		node.update(html);
		document.body.appendChild(node);
	},
	/**
	 * Reload the KDS GUI, in case we detect an "out-of-sync"
	 */
	reload: function() {
		sendLogMessage("INFO", "reload", "[kds] Reloading KDS UI");
		console.log("Reloading KDS UI");
		Try.these(
			(function(){window.location.reload();}),
			(function(){history.go(0);})
		);
	},
	discardOrder: function(order) { },
	/**
	 * Show list of KDSs that can be selected
	 */
	showKdsSwitchScreen: function() {
		if(!_main.selectableIds || !_main.selectableIds.length) {
			return;
		}
		if(!_main.switchKdsCont) {
			// create the switch screen if missing
			var mainbody = document.getElementsByTagName('body')[0];
			var frag = document.createDocumentFragment();
			var obj = document.createElement('div');
			var id = "switch_kds_cont";
			obj.style.display = 'none';
			frag.appendChild(obj);
			mainbody.insertBefore(frag, mainbody.firstChild);
			obj.setAttribute('id', id);
			_main.switchKdsCont = $(id);
			Element.addClassName(_main.switchKdsCont, 'switchKdsCont');
			var html = '<ul class="kdsList">';
			for(var i=0; i < _main.selectableIds.length; i++) {
				var kdsid = _main.selectableIds[i];
				html += '<li kdsid="' + kdsid + '" class="kdsItem">' + _main.kdsTitles[kdsid] + '</li>';
			}
			html += '</ul>';
			_main.switchKdsCont.update(html);
			disableTextSelection(_main.switchKdsCont);
		}
		if(_main.switchKdsTimeout) {
			clearTimeout(_main.switchKdsTimeout);
			_main.switchKdsTimeout = null;
		}
		// remove selected KDS class
		$$(".kdsSelected").each(function(item) { $(item).removeClassName("kdsSelected"); });
		$$('.kdsItem[kdsid="' + _main.switchKdsCurrent + '"]').each(function(item) { $(item).addClassName("kdsSelected"); });
		_main.switchKdsCont.show();
		_main.switchKdsTimeout = setTimeout(function() { _main.switchKdsCont.hide(); _main.switchKdsTimeout = null; }, 5000);
	},
	getHGap: function() {
		//default horizontal gap between cells. This function was created so that the hgap can be customized
		return 3;
	},
	getVGap: function() {
		//default vertical gap between cells. This function was created so that the hgap can be customized
		return 3;
	}
};

/**
 * Retrieves a value from the KDS model.
 * @param key {string} - model key
 * @return model value
 */
function getModelValue(key) {
	return _main.model.get(key);
}

/**
 * Display Javascript exception on screen
 * @param error {object} - exception object
 */
function notifyException(error) {
	if (error === null) {
		error = Error("Unexpected error");
	}
	var message = "";
	if (isError(error)) {
		message = "[kds] Error: Type='" + error.name + "' Message='" + error.message + "' ";
		if (error.fileName !== null) {
			message += "Script file='" + error.fileName + "' ";
		}
		if (error.lineNumber !== null) {
			message += "Line number=" + error.lineNumber + " ";
		}
		if (error.stack !== null) {
			message += "Stack trace:\n" + error.stack;
		}
	} else {
		message = "[kds] Error: '" + error + "'";
	}

	console.log(message);
	sendLogMessage("ERROR", "notifyException", message);
}

/**
 * Parses a I18N key an return the translated message.
 * @param key {String} - I18N with optional parameters separated by pipe. E.g.: "$MSG_CONFIRM_VALUE|123|456"
 */
function I18N(key) {
	if (!_main.i18nTable) return key; /* just happens on weird situations when the browser is reloading */
	if (key.startsWith("$")) {
		key = key.substring(1);
	} else { /* not I18N */
		return key;
	}
	var data = key.split("|");
	var msg = _main.i18nTable[data[0]];
	if (!msg) return key;
	for (var i=1; i<data.length; i++) {
		msg = msg.replace("{"+(i-1)+"}", data[i]);
	}
	return msg;
}

/**
 * Disable text selection for given element.
 * @param element {Object} - The element to disable text selection
 */
function disableTextSelection(element) {
	if(Prototype.Browser.IE) {
		element.onselectstart = function() { return false; };	// ie
	} else {
		element.onmousedown = function() { return false; };		// mozilla
	}
}

/** namespace for L10N (Localization) functions*/
L10N = {
	/* default localization rules */
	_rules: {decimalPlaces:2, currencyDecimalPlaces:2, decimalSep:".", thousandsSep:",", currencySymbol:"$ ",
	         dateTimeFormat: "yyyy-mm-dd HH:MM:ss", dateFormat: "yyyy-mm-dd", timeFormat: "HH:MM:ss"},
	/**
	 * Converts a currency string to a javascript Number object, using the current localization rules
	 * @param text: {String} - the currency string to convert
	 * @return {Number} - the parsed number, or NaN if the string was invalid
	 */
	currencyToNumber: function(text) {
		var rules = L10N._rules;
		return L10N._formatedToNumber(text, rules.currencyDecimalPlaces, rules.decimalSep, rules.thousandsSep);
	},
	/**
	 * Converts a javascript Number object to a formatted currency string, using the current localization rules
	 * @param number: {Number} - number to convert
	 * @param includeSymbol: {boolean} - if true, the currency symbol will be included (default: false)
	 * @return {String} - formatted currecy string
	 */
	numberToCurrency: function(number, includeSymbol) {
		var rules = L10N._rules;
		var text = L10N._numberToFormated(number, rules.currencyDecimalPlaces, rules.decimalSep, rules.thousandsSep);
		return includeSymbol ? (rules.currencySymbol + text) : text;
	},
	/**
	 * Converts a string to a javascript Number object, using the current localization rules
	 * @param text: {String} - the text string to convert
	 * @return {Number} - the parsed number, or NaN if the string was invalid
	 */
	textToNumber: function(text) {
		var rules = L10N._rules;
		return L10N._formatedToNumber(text, rules.decimalPlaces, rules.decimalSep, rules.thousandsSep);
	},
	/**
	 * Converts a javascript Number object to a formatted currency string, using the current localization rules
	 * @param number: {Number} - number to convert
	 * @return {String} - formatted currecy string
	 */
	numberToText: function(number) {
		var rules = L10N._rules;
		return L10N._numberToFormated(number, rules.decimalPlaces, rules.decimalSep, rules.thousandsSep);
	},
	/**
	 * Converts a javascript Date object to a formatted "date + time" string, using the current localization rules
	 * @param date: {Date} - date object to convert
	 * @return {String} - formatted date+time string
	 */
	dateTimeToText: function(date) {
		return date.format(L10N._rules.dateTimeFormat);
	},
	/**
	 * Converts a javascript Date object to a formatted "date-only" string, using the current localization rules
	 * @param date: {Date} - date object to convert
	 * @return {String} - formatted date-only string
	 */
	dateToText: function(date) {
		return date.format(L10N._rules.dateFormat);
	},
	/**
	 * Converts a javascript Date object to a formatted "time-only" string, using the current localization rules
	 * @param date: {Date} - date object to convert
	 * @return {String} - formatted time-only string
	 */
	timeToText: function(date) {
		return date.format(L10N._rules.timeFormat);
	},
	/** Reloads localization rules from the I18N table */
	_reloadRules: function() {
		function getval(str, defval){return _main.i18nTable[str] || defval;}
		L10N._rules = {
			decimalPlaces: 			Number(getval("L10N_DECIMAL_PLACES", "2")),
			currencyDecimalPlaces:	Number(getval("L10N_CURRENCY_DECIMALS"), "2"),
			currencySymbol:			getval("L10N_CURRENCY_SYMBOL", "$ "),
			decimalSep:				getval("L10N_DECIMALS_SEPARATOR", "."),
			thousandsSep:			getval("L10N_THOUSANDS_SEPARATOR", ","),
			dateTimeFormat:			getval("L10N_DATETIME_FORMAT", "yyyy-mm-dd HH:MM:ss"),
			dateFormat:				getval("L10N_DATE_FORMAT", "yyyy-mm-dd"),
			timeFormat:				getval("L10N_TIME_FORMAT", "HH:MM:ss")
		};
	},
	/** Internal function used to number formatting */
	_formatedToNumber: function(number, decimalPlaces, decimalSep, thousandsSep) {
		var deci = "";
		var split, i;
		// Gets sign
		if (number[0] == '-') {
			number = number.substring(1, number.length);
		}
		// Removes leading zeros
		number = number.gsub(/^0+/, "");
		for (i=0; i<number.length; i++) { // Check for invalid characters
			var ch = number[i] || number.substring(i, i+1); // IE does not accept "number[i]"
			if ("0123456789".indexOf(ch)==-1 && ch!=decimalSep && ch!=thousandsSep) {
				//return NaN; // Invalid number
			}
		}
		// Splits on decimals
		if (number.indexOf(decimalSep) != -1) {
			split = number.split(decimalSep);
			if (split.length != 2) return NaN; // Invalid number
			number = split[0];
			deci = split[1].substring(0, decimalPlaces);
		}
		// Validates thousands separators
		if (thousandsSep.length && number.indexOf(thousandsSep) != -1) {
			split = number.split(thousandsSep);
			if (split[0].length > 3 || split[0].length === 0) return NaN; // Invalid number
			for (i=1; i<split.length; i++) if (split[i].length != 3) return NaN; // Invalid number
			// Removes thousands separators
			number = number.gsub('\\'+thousandsSep, "");
		}
		return deci.length ? Number(number+'.'+deci) : Number(number);
	},
	/** Internal function used to number formatting */
	_numberToFormated: function(number, decimalPlaces, decimalSep, thousandsSep) {
		if (isNaN(number)) return "NaN";
		// Gets sign
		var sign = number<0 ? '-' : '';
		// Splits on decimals
		var split = String(Math.abs(number)).split('.');
		number = split[0];
		var dec = split.length==2 ? split[1].substring(0, decimalPlaces) : "";
		while (dec.length < decimalPlaces) dec += "0";
		// Adds thousands separators
		if (thousandsSep.length) {
			var sepPos = number.length-3;
			while (sepPos >= 1) {
				number = number.substring(0, sepPos)+thousandsSep+number.substring(sepPos, number.length);
				sepPos -= 3;
			}
		}
		// Adds decimals separator
		if (decimalSep.length) number += (decimalSep+dec);
		return sign+number;
	}
};

/**
 * Main entry point called when the page is loaded.
 */
function main() {
	if (!this.Prototype) {
		// Not everything loaded successfully, so lets try again
		Try.these(
			(function(){window.location.reload();}),
			(function(){history.go(0);})
		);
		return;
	}
	disableTextSelection(document.getElementsByTagName('body')[0]);
	document.title = "KDS";
	_main.load.defer();
}
