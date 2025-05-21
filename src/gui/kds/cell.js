var _tapped = false;                 /* marks if the window was tapped in a touch device */
var Cell = { cellCounter: 0 };

/**
 * Base KDS cell class. Is a basic <div> that implements methods to resize or move the element
 * using effects. It also capture click and double-click mouse events and calls the registered callback.
 */
Cell.Base = Class.create({
	x: 0,							/* x position inside the container <div> */
	y: 0,							/* y position inside the container <div> */
	width: 0,						/* cell width */
	height: 0,						/* cell height */
	visible: false,					/* visibility flag */
	effectState: "off",				/* level of effects (currently can be "on" or "off") */
	onClickCallback: null,			/* on mouse click callback */
	onDoubleClickCallback: null,	/* on mouse double-click callback */
	_cellContainer: null,			/* main <div> element */
	_cellId: "",					/* cell id generated from global cellCounter */
	/**
	 * Creates the main <div> assigning an id and bind event listeners
	 */
	initialize: function() {
		var mainbody = $('main_body_div');
		var frag = document.createDocumentFragment();
		this._cellId = "cell" + (++Cell.cellCounter);
		var obj = document.createElement('div');
		obj.style.display = 'none';
		frag.appendChild(obj);
		mainbody.insertBefore(frag, mainbody.firstChild);
		obj.setAttribute('id', this._cellId + "_cont");
		this._cellContainer = $(this._cellId + "_cont");
		this._cellContainer.style.position = 'absolute';
		Element.addClassName(this._cellContainer, 'cell');
		this._cellContainer.observe('dblclick', this._onDoubleClick.bindAsEventListener(this));
		this._cellContainer.observe('mousedown', this._onMouseup.bindAsEventListener(this));
		this._cellContainer.observe('touchstart', this._onTouchStart.bindAsEventListener(this));
		disableTextSelection(this._cellContainer);
	},
	/**
	 * Return main <div> element
	 */
	getContainer: function() {
		return(this._cellContainer);
	},
	/**
	 * Return current cell visibility state
	 */
	isVisible: function() {
		return(this.visible);
	},
	/**
	 * Return current cell width
	 */
	getWidth: function() {
		return(this.width);
	},
	/**
	 * Return current cell height
	 */
	getHeight: function() {
		return(this.height);
	},
	/**
	 * Return current cell x position
	 */
	getLeft: function() {
		return(this.x);
	},
	/**
	 * Return current cell y position
	 */
	getTop: function() {
		return(this.y);
	},
	getCellSize: function() {
		if (this._bodyCol.length === 0) {
			//need to calculate how many cells the order uses
			this.redrawItems();
		}
		var size = 0;
		for(var i = 0; i < this._bodyCol.length; i++) {
			if (this._bodyCol[i] !== undefined) {
				size++;
			}
		}
		return size;
	},
	/**
	 * Set cell size without effects
	 * @param width {integer} - Cell width to set in pixels
	 * @param height {integer} - Cell height to set in pixels
	 */
	setSize: function(width, height) {
		this._cellContainer.style.width = width + 'px';
		this._cellContainer.style.height = height + 'px';
	},
	/**
	 * Set cell position without effects
	 * @param left {integer} - Cell left position to set in pixels
	 * @param top {integer} - Cell top position to set in pixels
	 */
	setPos: function(left, top) {
		this._cellContainer.style.left = left + 'px';
		this._cellContainer.style.top = top + 'px';
	},
	/**
	 * Show cell using effects when effectState is set to "on"
	 */
	show: function() {
		this.visible = true;
		if(this.effectState == "on") {
			new Effect.Appear(this._cellContainer, { duration: 0.2, queue: { position: 'end', scope: this._cellId + "_show" } });
		} else {
			this._cellContainer.show();
		}
	},
	/**
	 * Hide cell using effects when effectState is set to "on"
	 */
	hide: function(afterHide) {
		this.visible = false;
		if(this.effectState == "on") {
			new Effect.Fade(this._cellContainer, { duration: 0.2, queue: { position: 'end', scope: this._cellId + "_show" }, afterFinish: function() { if(afterHide) afterHide(this); } });
		} else {
			this._cellContainer.hide();
			if(afterHide) {
				afterHide(this);
			}
		}
	},
	hideCell: function() {
		this.hide();
		if (this._contdCell) {
			this._contdCell.each(function(item) {
				item.value.hide();
			});
		}
	},
	/**
	 * Move cell using effects when effectState is set to "on"
	 * @param left {integer} - Cell left position to set in pixels
	 * @param top {integer} - Cell top position to set in pixels
	 */
	move: function(left, top) {
		if(this.effectState == "on") {
			new Effect.Move(this._cellContainer, { x: left, y: top, mode: 'absolute', queue: { position: 'end', scope: this._cellId + "_move" } });
		} else {
			this.setPos(left, top);
		}
	},
	/**
	 * Resize cell using effects when effectState is set to "on"
	 * @param width {integer} - Cell width to set in pixels
	 * @param height {integer} - Cell height to set in pixels
	 */
	resize: function(width, height) {
		if(this.effectState == "on") {
			new Effect.Morph(this._cellContainer, {
				style: {
					width: width + 'px',
					height: height + 'px'
				},
				queue: { position: 'end', scope: this._cellId + "_size" }
			});
		} else {
			this.setSize(width, height);
		}
	},
	/**
	 * Set font size
	 * @param size {integer} - The font size to set in pixels
	 */
	setFontSize: function(size) {
		this._cellContainer.style.fontSize = size + 'px';
	},
	/**
	 * Stops any running effect of current cell
	 */
	stopEffects: function() {
		if(this.effectState != "off") {
			var effectTypes = ["_size", "_show", "_move"];
			for (var index in effectTypes) {
				var type = effectTypes[index];
				var queue = Effect.Queues.get(this._cellId + type);
				queue.effects.clear();
				queue.remove(null);		/* force the queue to clear interval */
			}
		}
	},
	/**
	 * Set effect state
	 * @param state {string} - The effect state to set ("on" or "off")
	 */
	setEffects: function(state) {
		this.effectState = state;
	},
	/**
	 * Set mouse click callback function
	 * @param callback {function} - The function to be called on click
	 */
	setClickListener: function(callback) {
		this.onClickCallback = callback;
	},
	/**
	 * Set mouse double-click callback function
	 * @param callback {function} - The function to be called on double-click
	 */
	setDoubleClickListener: function(callback) {
		this.onDoubleClickCallback = callback;
	},
	/**
	 * Internal function called by the event listener that calls the registered callback
	 */
	_onDoubleClick: function(event) {
		if(this.onDoubleClickCallback) {
			this.onDoubleClickCallback(this);
		}
	},
	/**
	 * Internal function called by the event listener that calls the registered callback
	 */
	_onMouseup: function(event) {
		if(this.onClickCallback) {
			this.onClickCallback(this);
		}
	},
	_onTouchStart: function(event) {
        if(_tapped == false) {
            _tapped = true;
            setTimeout( function() { _tapped = false; }, 300 );
            return false;
        }
        event.preventDefault();
        if(this.onDoubleClickCallback) {
            this.onDoubleClickCallback(this);
        }
    }
});

/**
 * This class represents an order cell, or a continuation cell (when the order continues in a different row)
 */
Cell.Sale = Class.create(Cell.Base, {
	orderId: -1,			/* order id asociated to this cell */
	state: "",				/* current order state */
	productionState: "",	/* current production state */
	creationDate: null,		/* order creation date */
	timeStr: "",			/* time string */
	maxColSpan: -1,			/* maximum column span (-1 unlimited) */
	colSpan: 0,				/* current column span, calculated by setCellHints */
	maxBodyCols: 0,			/* number of columns allowed to display, calculated by setCellHints */
	cellHeight: 0,			/* single cell height */
	cellWidth: 0,			/* single cell width */
	bodyHeight: [],			/* single cell body height, per column */
	lineHeight: 0,			/* single item line height */
	linesPerCell: [],		/* number of lines per cell, per column */
	imageLinesQty: 0,		/* quantity of lines to reserve for the order image (picture) - 0 means disabled */
	lines: null,			/* array of line items (complete sale) */
	thresholds: null,		/* hash of thresholds (key: id, value: timeout in milliseconds) */
	draggable: null,		/* draggable object */
	displayOrder: -1,		/* display order from production subsystem */
	major: -1,				/* order major */
	minor: -1,				/* order minor */
	pod: "",				/* point of distribution (FC, DT, etc) */
	saleType: "",			/* sale type (EAT_IN, TAKE_OUT) */
	totalAmount: "",		/* total amount */
	taxAmount: "",			/* tax amount */
	posId: -1,				/* POS id */
	operatorName: "",		/* operator name */
	multiorderFlag: false,	/* flag indicating if this order is part of a "multi-order" */
	properties: [],         /* order properties xml element */
	custom: [],				/* custom tags (JIT specific) */
	onStartDrag: null,		/* user defined function to be called when a drag is initiated */
	onEndDrag: null,		/* user defined function to be called when a drag is ended */
	onRevertDrag: null,		/* user defined function to be called when a drag is reverted */
	selectedLine: 0,		/* currently selected line */
	showTimer: true,		/* whether the order timer must be displayed */
	moreItems: false,		/* whether the order has more items than it's possible to display*/
	recalled: false,		/* Whether the order was recalled after being served */
	_showContRight: false,	/* show continuation icon on the right */
	_showMoreIcon: false,	/* show more icon on the right */
	_header: null,			/* header object */
	_bodyCol: null,			/* array of body column objects */
	_footer: null,			/* footer object */
	_contdCell: null,		/* array of cell continuation (when the order needs to appear in the next row) */
	/**
	 * Helper function to convert an XML object into a string
	 * @param elem {object} - XML object
	 */
	XMLtoString: function(elem) {
		var serialized;
		try {
			/* XMLSerializer exists in current Mozilla browsers */
			serializer = new XMLSerializer();
			serialized = serializer.serializeToString(elem);
		} catch (e) {
			/* IE has a different approach to serializing XML */
			serialized = elem.xml;
		}
		return(serialized);
	},
	/**
	 * Initialize cell, create internal objects (e.g. header, footer)
	 * @param elem {object} - XML object
	 */
	initialize: function($super, xml) {
		$super();
		var html = "<table id=\"" + this._cellId + "_header_table\" class=\"saleCellHeader\"><tr>" +
			"<td><div class=\"saleCellHeaderContdLeft\" id=\"" + this._cellId + "_header_contd_left" + "\" style=\"display: none\"><img src=\"images/contd_left.png\"/></div></td>" +
			"<td><div class=\"saleCellHeaderLabel\" id=\"" + this._cellId + "_header" + "\"></div></td>" +
			"<td class=\"saleCellHeaderContdRight\"><div class=\"saleCellHeaderContdRight\" id=\"" + this._cellId + "_header_contd_right" + "\"></div></td>" +
			"</tr></table>" +
			"<div id=\"" + this._cellId + "_footer_cont\"" + " class=\"saleCellFooter\">" +
			"<div class=\"saleCellFooterLabel\" id=\"" + this._cellId + "_footer" + "\"></div>" +
			"<div class=\"saleCellFooterMore\" id=\"" + this._cellId + "_footer_more" + "\" style=\"display: none\">MORE...</div>" +
			"</div>";
		this._bodyCol = new Array();
		this._contdCell = new Hash();
		this.getContainer().update(html);
		this._header_table = $(this._cellId + "_header_table");
		this._header = $(this._cellId + "_header");
		this._footer_table = $(this._cellId + "_footer_cont");
		this._footer = $(this._cellId + "_footer");
		this.creationDate = new Date();
		this.lines = new Array();
		this.updateSale(xml);
		this.updateTime();
		this.draggable = new Draggable(this.getContainer(), { revert: this.revertDrag.bind(this),
			onStart: function(draggable, event) {
				this.startDrag();
			}.bind(this),
			onEnd: function(draggable, event) {
				this.endDrag();
			}.bind(this)
		});
		if (typeof(custom) == "object" && custom.initializeCell != null) {
		    custom.initializeCell(this);
		}
	},
	/**
	 * Recurse <Item> nodes from a <ProductionOrder>, adding formatted line to this.lines array
	 * @param node {object} - Item node
	 * @param level {int} - Recursivity level used to generate the indentation
	 * @param parentQty {int} - Quantity of items in the base parent used during render to strike void items and its subitems
	 */
	addItemsRecursively: function(node, level, parentQty) { },
	/**
	 * Fill array containing item lines and update footer
	 * @param xml {object} - XML object contatining a <ProductionOrder>, or null (empty cell)
	 */
	updateSale: function(xml) { },
	selectNextLine: function() {
		if (!_main.enableTagging || !this.lines || !this.lines.length) {
			return;
		}
		var currentFound = false;
		var firstLine = 0;
		for(var i=0; i < this.lines.length; i++) {
			var line = this.lines[i];
			if(line.striked) {
				continue;
			}
			if(firstLine === 0) {
				firstLine = line.line_number;
			}
			if(line.line_number == this.selectedLine) {
				currentFound = true;
			}
			if(currentFound && line.line_number != this.selectedLine) {
				this.selectedLine = line.line_number;
				return;
			}
		}
		this.selectedLine = firstLine;
		return;
	},
	selectPreviousLine: function() {
		if (!_main.enableTagging || !this.lines || !this.lines.length) {
			return;
		}
		var currentFound = false;
		var lastLine = 0;
		for(var i=this.lines.length - 1; i >= 0; i--) {
			var line = this.lines[i];
			if(line.striked) {
				continue;
			}
			if(lastLine === 0) {
				lastLine = line.line_number;
			}
			if(line.line_number == this.selectedLine) {
				currentFound = true;
			}
			if(currentFound && line.line_number != this.selectedLine) {
				this.selectedLine = line.line_number;
				return;
			}
		}
		this.selectedLine = lastLine;
		return;
	},
	updateCreationDate: function(ponode) { },
	/**
	 * Sets the style that this cell must display according to its state
	 */
	checkColors: function() {
		this.checkHeld();
		this.checkVoided();
		this.checkThresholds();
		this.checkRecall();
	},
	/**
	 * Redaw (and create if necessary) cell column items.
	 * This function uses line items in the array filled by updateSale.
	 * Note that it will have effect only if setCellHints was called previously (linesPerCell was calculated).
	 */
	redrawItems: function() {
		var len = this.lines.length;
		if(this.linesPerCell.length > 0) {
			var i=0, bodyCol=0, offset=0;
			/* iterate by body columns */
			for(bodyCol = 0; bodyCol < this.maxBodyCols; bodyCol++) {
				var linesPerCell = this.linesPerCell[bodyCol];
				/* consider lines taken by the image on the first column */
				if (this.imageLinesQty>0 && bodyCol==0) {
					linesPerCell -= this.imageLinesQty;
				}
				/* put the line items into a table */
				var html = "<table class=\"cellSale\" style=\"height: " + this.bodyHeight[bodyCol] + "px\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\"><tbody>\n";
				/* add the order image right before the items, if necessary */
				if (this.imageLinesQty > 0 && bodyCol==0) {
					var imgurl = "";
					var cachedImg = _main.orderImages[this.orderId];
					if (cachedImg && cachedImg.md5 == this.imageMd5) {
						// The image is already on cache, just show it...
						imgurl = cachedImg.url;
					} else {
						// The image is not on cache, or it has changed. retrieve it
						var data = String(this.orderId) + '\0' + "url/base64";
						// Set a temporary (empty)  image, while it is being retriever - this avoids multiple requests
						_main.orderImages[this.orderId] = {md5: this.imageMd5, url: ""};
						if (this.imageMd5 && this.imageMd5.length) {
							// Send a message to get the image data
							sendMessage("ProductionSystem", "ProductionSystem", "TK_PROD_RETRIEVEIMAGE", FM_PARAM, -1, data, function(req) {
								var cachedImg = {md5: this.imageMd5, url: req.responseText}
								_main.orderImages[this.orderId] = cachedImg;
								// The image has been retrieved, show it...
								var img = $('orderimage_'+this.orderId);
								if (img) img.src = cachedImg.url;
							}.bind(this));
						}
					}
					var srcattr = (imgurl.length ? 'src="'+imgurl+'"' : '');
					html += '<tr><td><img id="orderimage_'+this.orderId+'" '+srcattr+' width="'+this.cellWidth+'px" height="'+(this.imageLinesQty*this.lineHeight)+'px"></td></tr>\n';
				}
				for(i = offset; (i < len) && (i < (offset + linesPerCell)); i++) {
					var line = this.lines[i];
					var itemClass = this.defineItemClass(line);
					var lineClass = "";
					if (_main.enableTagging && this.selectedLine == line.line_number) {
						lineClass = "cellSelectedLine";
					}
					html += this.createItemHtml(lineClass, itemClass, line);
				}
				/* fill remaining lines with spaces */
				for(; i < (offset + linesPerCell); i++) {
					html += "<tr><td>&nbsp;</td></tr>\n";
				}
				html += "</tbody></table>\n";
				/* set the offset for the next column */
				offset = i;
				/* create body column if necessary */
				if(this._bodyCol[bodyCol] == null) {
					var htmlDiv = "<div class=\"saleCellBody\" style=\"display: none; padding-top: " + (_main.cellPadding || "0") + "px;\" id=\"" + this._cellId + "_body_" + bodyCol + "\"></div>";
					this.getContainer().insert({ top: htmlDiv });
					this._bodyCol[bodyCol] = $(this._cellId + "_body_" + bodyCol);
				}
				this._bodyCol[bodyCol].update(html);
				this._bodyCol[bodyCol].style.width = this.cellWidth + "px";
				this._bodyCol[bodyCol].style.height = this.bodyHeight[bodyCol] + "px";
				this._bodyCol[bodyCol].show();
			}
			/* hide unused cols */
			len = this._bodyCol.length;
			for(; bodyCol < len; bodyCol++) {
				if(this._bodyCol[bodyCol] != null) {
					this._bodyCol[bodyCol].hide();
				}
			}
		}
	},
	/**
	 * Define the CSS class for an item
	 */
	defineItemClass: function(line) {
		var itemClass;
		if (line.striked === true) {
			itemClass = "ellipsisStrike";
		} else if (line.added === true) {
			itemClass = "itemAdded";
		} else {
			itemClass = "ellipsis";
		}
		return itemClass;
	},
	/**
	 * Creates the HTML string representing the item
	 */
	createItemHtml: function(lineClass, itemClass, line) {
		return "<tr class=\"" + lineClass + "\"><td><div class=\"" + itemClass + "\" style=\"width: " + this.cellWidth + "px; height: " + this.lineHeight + "px;\"><div class=\"innerDiv\"><i class=\"untaggedIcon " + ((this.taggedLines.indexOf(line.line_number) >= 0) ? "taggedIcon" : "") + " fa fa-check\" aria-hidden=\"true\"></i>" + line.line + "</div></div></td></tr>\n";
	},
	/**
	 * Get a Cell.Sale for a given row. If necessary it creates a new one copying properties.
	 * Row 0 is the row where the sale started, > 0 is a continuation of the main cell.
	 */
	getCellByRow: function(row) { },
	/**
	 * Get a body column object (contains a table with items to display in that cell column)
	 * @param colIndex {integer} - the index of the column to return between 1 and maxBodyCols
	 */
	getBodyColumn: function(colIndex) {
		if(this._bodyCol[colIndex]) {
			return(this._bodyCol[colIndex]);
		}
		return(null);
	},
	/**
	 * Update order time
	 */
	updateTime: function() {
		this.timeStr = "";
		if (this.showTimer === true) {
			var diff = (new Date().getTime() - this.creationDate.getTime());
			var negative = diff<0;
			if (negative) diff = Math.abs(diff);
			var hours = parseInt(diff/3600000);
			var mins = parseInt(diff/60000)%60;
			var secs = parseInt(diff/1000)%60;
			this.timeStr = (negative ? "-" : "");
			if(hours > 0) {
				this.timeStr = padDigits(hours, 2) + ":";
			}
			this.timeStr += padDigits(mins, 2) + ":" + padDigits(secs, 2);
			this.checkThresholds();
		}
		this.updateHeader();
	},
	/**
	 * Update order header
	 */
	updateHeader: function() {
		if (this.getOrderId() == -1) {
			this._header.update("&nbsp;");
			return;
		}
		if (!_main.i18nTable.cellHeaderFmtLoc) {
			/* convert I18N entries in the format string */
			_main.i18nTable.cellHeaderFmtLoc = _main.cellHeaderFmt.gsub(/(\$\w+)/, function(match) {
				return I18N(match[1]);
			});
		}
		var fn = this.parseCustomFunction(_main.i18nTable.cellHeaderFmtLoc);
		if (fn) {
			fn(this, this._header);
		} else {
			this._header.update(this.parseMacros(_main.i18nTable.cellHeaderFmtLoc));
		}
	},
	/**
	 * Update footer status text
	 */
	updateFooter: function() {
		if (!_main.i18nTable.cellFooterFmtLoc) {
			/* convert I18N entries in the format string */
			_main.i18nTable.cellFooterFmtLoc = _main.cellFooterFmt.gsub(/(\$\w+)/, function(match) {
				return I18N(match[1]);
			});
		}
		var fn = this.parseCustomFunction(_main.i18nTable.cellFooterFmtLoc);
		if (fn) {
			fn(this, this._footer);
		} else {
			this._footer.update(this.parseMacros(_main.i18nTable.cellFooterFmtLoc));
		}
		if (this.recalled === true) {
			this._footer.update(this._footer.innerText + "  " + I18N("$KDS_RECALL"));
		}
		if (this.multiorderFlag) {
			this._footer.up().addClassName("multiOrder");
		} else {
			this._footer.up().removeClassName("multiOrder");
		}
	},
	parseCustomFunction: function(template) { },
	/**
	 * Parse the macros on the given template, and return a formatted resulting string
	 */
	parseMacros: function(template) {
		return template.gsub(/#\{(.*?)\}/, function(match) {
			/* this is the macro being replaced */
			var macro = match[1].toLowerCase();
			/* try to find the % sign that indicates how to format numbers */
			var index = macro.indexOf("%");
			var mod = null;
			var pad = false;
			if (index != -1) {
				/* this is the module that should be applied */
				mod = macro.substring(index+1);
				/* if the module starts with a zero, then we should zero-pad the number after we finish */
				if (mod[0]=="0") pad = true;
				mod = Number(mod) || null;
				/* remove the %xxx from the macro */
				macro = macro.substring(0,index);
			}
			var value = null;
			/* determine the value of the macro */
			switch (macro) {
				case "id":		value = this.orderId; break;
				case "major":	value = this.major; break;
				case "minor":	value = this.minor; break;
				case "pod":		value = I18N("$"+this.pod); break;
				case "saletype":value = I18N("$"+this.saleType); break;
				case "total":	value = L10N.numberToCurrency(Number(this.totalAmount),true); break;
				case "tax":		value = L10N.numberToCurrency(Number(this.taxAmount),true); break;
				case "posid":	value = this.posId; break;
				case "time":	value = this.timeStr; break;
				case "status":	value = I18N("$STATUS_" + this.getState()); break;
			}
			if (value === null && macro.indexOf("property:") === 0) {
			    var key = match[1].substring("property:".length); //we need the unaltered custom field name
			    if (key !== "") {
                    value = this.getOrderProperty(key);
			    }
			    var i18nkey = "$KDS_PROPERTY_" + value;
			    var i18nvalue = I18N(i18nkey);
			    if (("$" + i18nvalue) != i18nkey) {
			    	value = i18nvalue;
			    }
			}
			/* if we have a value and a module, apply the module on the value */
			if (value!=null && mod) {
				value = String(parseInt(value) % mod);
				/* check if we need to zero-pad the number */
				if (pad) {
					value = padDigits(value, (String(mod).length - 1));
				}
			}
			return (value!=null) ? value : ("#{"+match[1]+"}");
		}.bind(this));
	},
	/**
	 * Helper function to remove all threshold styles from the main <div>
	 */
	removeOldThresholdClasses: function() {
		/* remove any previous threshold class */
		var toRemove = new Array();
		var classNames = this.getContainer().className;
		if (classNames.indexOf("saleCellThreshold") == -1) {
			return;
		}
		$w(classNames).each(function(clazzName) {
			if(clazzName.indexOf("saleCellThreshold") != -1) {
				toRemove.push(clazzName);
			}
		});
		for(var i=0; i<toRemove.length; i++) {
			this.getContainer().removeClassName(toRemove[i]);
		}
	},
	/**
	 * Check and set current threshold class style
	 */
	checkThresholds: function() {
		if(!this.thresholds || this.showTimer === false) {
			return;
		}
		if(this.recalled !== true && (this.getState() != "VOIDED") && (this.getProductionState() != "HELD")) {
			var now = new Date();
			var diff = now.getTime() - this.creationDate.getTime();
			var thresholdId = -1;
			var lastTimeout = 0;
			/* find latest threshold */
			this.thresholds.each(function(pair) {
				if((diff > pair.value) && (pair.value > lastTimeout)) {
					thresholdId = pair.key;
					lastTimeout = pair.value;
				}
			});
			if(thresholdId != -1) {
				var classToAdd = 'saleCellThreshold' + padDigits(thresholdId, 2);
				if(!this.getContainer().hasClassName(classToAdd)) {
					this.removeOldThresholdClasses();
					this.getContainer().addClassName(classToAdd);
					this._contdCell.each(function(cell) {
						cell.value.checkThresholds();
					});
				}
			} else {
				this.removeOldThresholdClasses();
			}
		}
	},
	/**
	 * Check and apply voided class style
	 */
	checkVoided: function() { },
	/**
	 * Check and apply held class style
	 */
	checkHeld: function() {
		/* check for voided and update class */
		if(this.getProductionState() == "HELD") {
			this.removeOldThresholdClasses();
			/* add cell held class */
			this.getContainer().addClassName('saleCellHeld');
		} else {
			this.getContainer().removeClassName('saleCellHeld');
		}
		this._contdCell.each(function(cell) {
			cell.value.checkHeld();
		});
	},
	/**
	 * Check and apply voided class style
	 */
	checkRecall: function() { },
	/**
	 * Get current order id from production subsystem
	 */
	getOrderId: function() {
		return(this.orderId);
	},
	/**
	 * Set current order state
	 */
	setOrderId: function(id) {
		this.orderId = id;
	},
	/**
	 * Calculate element dimensions according to parameters
	 * @param width {integer} - Single cell width
	 * @param height {integer} - Single cell height
	 * @param lines {integer} - Maximum number of lines to display per cell
	 * @param imageLines {integer} - Number of lines to reserve for the order image/picture (0 means disabled)
	 * @param headerLines {integer} - Number of lines reserved for header
	 * @param footerLines {integer} - Number of lines reserved for footer
	 * @param headerColumns {integer} - Number of columns in which the header must be displayed (-1 means all = default)
	 */
	setCellHints: function(width, height, lines, imageLines, headerLines, footerLines, headerColumns) {
		padding = _main.cellPadding * 2; //style.padding * 2; // top and bottom
		this.cellHeight = height;
		this.cellWidth = width - _main.cellPadding;
		this.imageLinesQty = imageLines;
		this.lineHeight = this.cellHeight / lines;
		this.headerLines = headerLines;
		this.footerLines = footerLines;
		this.headerColumns = headerColumns;
		/* calculate cell span */
		var headerWidth = "100%";
		var headerHeight = this.lineHeight * headerLines;
		var footerHeight = this.lineHeight * footerLines;
		if(this.lines) {
			// headerColumns == -1 means that the header is spanned through all columns
			if (headerColumns < 0) {
				this.colSpan = Math.ceil((this.lines.length + imageLines) / (lines - (headerLines + footerLines)));
			} else {
				this.colSpan = Math.ceil((this.lines.length + imageLines + (headerLines * headerColumns)) / (lines - footerLines));
				headerWidth = this.cellWidth + "px";
			}
			if(this.colSpan <= 0) {
				this.colSpan = 1;
			}
			this.maxBodyCols = ((this.maxColSpan) > 0 && (this.maxColSpan < this.colSpan)) ? this.maxColSpan : this.colSpan;
		}
		this._header_table.style.width = headerWidth;
		this._header_table.style.height = headerHeight + "px";
		if (!footerLines) {
			this._footer_table.style.height = "0px";
		}
		this.linesPerCell = [];
		this.bodyHeight = [];
		for(var i = 0; i < this.colSpan; i++) {
			this.linesPerCell.push((headerColumns < 0) ? (lines - (headerLines + footerLines)) : (((i + 1) <= headerColumns) ? (lines - (headerLines + footerLines)) : (lines - footerLines)));
			this.bodyHeight.push(this.cellHeight - headerHeight - footerHeight);
		}
	},
	/**
	 * Sets the maximum number of column spans per cell
	 * @param maxColSpan {integer} - Maximum number of column spans per cell
	 */
	setMaxColSpan: function(maxColSpan) {
		this.maxColSpan = maxColSpan;
	},
	/**
	 * Get current order state
	 */
	getState: function() {
		return(this.state);
	},
	/**
	 * Set current order state
	 */
	setState: function(state) {
		this.state = state;
		this._contdCell.each(function(cell) {
			cell.value.setState(state);
		});
	},
	/**
	 * Get current production state
	 */
	getProductionState: function() {
		return(this.productionState);
	},
	/**
	 * Set current production state
	 */
	setProductionState: function(state) {
		this.productionState = state;
		this._contdCell.each(function(cell) {
			cell.value.setProductionState(state);
		});
	},
	/**
	 * Get current display order
	 */
	getDisplayOrder: function() {
		return(this.displayOrder);
	},
	/**
	 * Set current display order
	 * @param order {integer} - The display order coming from production
	 */
	setDisplayOrder: function(order) {
		this.displayOrder = order;
	},
	/**
	 * Set order properties array
	 * @param properties {array} - The array with order properties
	 */
	setProperties: function(properties) {
		this.properties = properties;
	},
	/**
	 * Set order properties array
	 * @param properties {array} - The array with order properties
	 */
	getOrderProperty: function(key) {
		for(var i = 0; i < this.properties.length; i++) {
		    if (this.properties[i].getAttribute("key") == key) {
		        return this.properties[i].getAttribute("value");
		    }
		}
		return "";
	},
	/**
	 * Show "MORE..." label
	 */
	showMoreLabel: function() {
		$(this._cellId + "_footer_more").show();
		this.moreItems = true;
	},
	/**
	 * Hide "MORE..." label
	 */
	hideMoreLabel: function() {
		$(this._cellId + "_footer_more").hide();
		this.moreItems = false;
	},
	hasMoreItems: function() {
		if (this.moreItems === true) {
			return true;
		}
		if (this._contdCell !== undefined) {
			var values = this._contdCell.values();
			for (var i = 0; i < values.length; i++) {
				if (values[i].moreItems === true) {
					return true;
				}
			}
		}
		return false;
	},
	markClippedCells: function(index) {
		for(var i = 0; i < index; i++) {
			if (this._bodyCol[i] !== undefined) {
				this._bodyCol[i].addClassName("clippedCell");
			}
		}
	},
	clearClippedCells: function() {
		for(var i = 0; i < this._bodyCol.length; i++) {
			this._bodyCol[i].removeClassName("clippedCell");
		}
	},
	/**
	 * Show continuation icon on the left side of the header
	 */
	showContdLeft: function() {
		$(this._cellId + "_header_contd_left").show();
	},
	/**
	 * Hide continuation icon on the left side of the header
	 */
	hideContdLeft: function() {
		$(this._cellId + "_header_contd_left").hide();
	},
	/**
	 * Show an icon on the right side of the header.
	 * Depending on current flags can be "continuation" or "more" icon.
	 */
	showIconRight: function() {
		var className = "";
		if(this._showContRight) {
			className = "continuedRight";
		}
		if(this._showMoreIcon) {
			className = "moreOrders";
		}
		if(className !== "") {
			var icon = $(this._cellId + "_header_contd_right");
			icon.removeClassName("continuedRight moreOrders");
			icon.addClassName(className);
			icon.show();
		}
	},
	/**
	 * Hide the icon on the right side of the header.
	 */
	hideIconRight: function() { },
	/**
	 * Show "continuation" icon on the right side of the header
	 */
	showContdRight: function() {
		this._showContRight = true;
		this.showIconRight();
	},
	/**
	 * Hide "continuation" icon on the right side of the header
	 */
	hideContdRight: function() {
		this._showContRight = false;
		this.hideIconRight();
	},
	/**
	 * Show "more" icon on the right side of the header
	 */
	showMoreIcon: function() {
		this._showMoreIcon = true;
		this.showIconRight();
	},
	/**
	 * Hide "more" icon on the right side of the header
	 */
	hideMoreIcon: function() {
		this._showMoreIcon = false;
		this.hideIconRight();
	},
	/**
	 * Stops any running effect
	 */
	stopEffects: function($super) {
		$super();
		this._contdCell.each(function(cell) {
			cell.value.stopEffects();
		});
	},
	clearCell: function() {
		this._showContRight = false;
		this._showMoreIcon = false;
		this.recalled = false;
		this.hideIconRight();
		this.hideContdLeft();
		this.getContainer().removeClass();
		var icon = $(this._cellId + "_header_contd_right");
		icon.removeClassName("continuedRight");
		icon.removeClassName("moreOrders");
		var i = 0;
		for (;i < this._bodyCol.length;i++) {
			if (this._bodyCol[i] !== undefined) {
				this._bodyCol[i].innerHTML = "";
				this._bodyCol[i].hide();
				delete this._bodyCol[i];
			}
		}
		if (this._contdCell !== undefined) {
			keys = this._contdCell.keys();
			for(i = 0; i < keys.length; i++) {
				var value = this._contdCell.get(keys[i]);
				if (value !== undefined) {
					value.innerHTML = "";
					value.hide();
					this._contdCell.unset(keys[i]);
				}
			}
		}
	},
	/**
	 * Bump cell
	 * @param afterBump {function} - A function to be called after the bump
	 */
	bump: function(afterBump) {
		this.onStartDrag = null;	// avoid dragging after bump
		this.stopEffects();
		this._contdCell.each(function(cell) {
			cell.value.bump();
		});
		this.hide(function(cell) {
			if(afterBump) {
				afterBump();
			}
			cell.setOrderId(-1);
		});
	},
	/**
	 * Set or unset focus style
	 * @param focus {boolean} - true to set the focus, false to unset
	 */
	setFocus: function(focus) {
		var table = $(this._cellId + "_header_table");
		if(table) {
			if(focus) {
				table.addClassName('saleCellHeaderFocus');
			} else {
				table.removeClassName('saleCellHeaderFocus');
			}
		}
		this._contdCell.each(function(cell) {
			cell.value.setFocus(focus);
		});
	},
	/**
	 * Set start drag listener
	 * @param callback {function} - Function to be called when the drag cell action begins
	 */
	setStartDragListener: function(callback) {
		this.onStartDrag = callback;
	},
	/**
	 * Internal function called by the event listener when the drag cell action begins
	 * This function calls the registered callback, if any
	 */
	startDrag: function() {
		if(this.onStartDrag) {
			this.stopEffects();
			this.onStartDrag(this);
		}
	},
	/**
	 * Set end drag listener
	 * @param callback {function} - Function to be called when the cell is released in a droppable
	 */
	setEndDragListener: function(callback) {
		this.onEndDrag = callback;
	},
	/**
	 * Internal function called by the event listener when the drag cell is released in a droppable
	 * This function calls the registered callback, if any
	 */
	endDrag: function() {
		if(this.onEndDrag) {
			this.onEndDrag(this);
		}
	},
	/**
	 * Set revert drag listener
	 * @param callback {function} - Function to be called when the cell is released in a non-droppable
	 */
	setRevertDragListener: function(callback) {
		this.onRevertDrag = callback;
	},
	/**
	 * Internal function called by the event listener when the drag cell is released in a non-droppable
	 * This function calls the registered callback, if any
	 */
	revertDrag: function(obj) {
		if(this.onRevertDrag) {
			this.onRevertDrag(this);
		}
	},
	/**
	 * Set threshold times
	 * @param thresholds {integer} - Hash table containing the threshold times
	 */
	setThresholds: function(thresholds) {
		this.thresholds = thresholds;
	},
    printOrder: function() {
        var params = "" + '\0' + this.orderId;
        sendMessage("ORDERMGR" + this.posId,"ORDERMGR","TK_SLCTRL_OMGR_ORDERPICT",FM_PARAM,-1,params,this.orderPictureCallback.bind(this));
    },
    orderPictureCallback: function(request) {
        var order = request.responseText.split('\0')[2];
        var params = _main.model.get("REPORT") + '\0' + order;
        sendMessage("ReportsGenerator","ReportsGenerator","TK_REPORT_GENERATE",FM_PARAM,-1,params, this.generateReportCallback.bind(this));
    },
    generateReportCallback: function(request) {
        sendMessage(_main.model.get("PRINTER"),"printer","TK_PRN_PRINT", FM_STRING,-1,request.responseText);
	},
	/**
	 * Return number of lines reserved for header for a given cell column.
	 */
	getHeaderLines: function(col) {
		if (this.headerColumns < 0 || ((col + 1) <= this.headerColumns)) {
			// -1 means that the header expands to all the cell columns
			return this.headerLines;
		}
		// this column does not have lines reserved for header
		return 0;
	},
	lineHasChild: function(lineNumber) {
		if (!this.lines || !this.lines.length) {
			return false;
		}
		var hasChild = false;
		for(var i=0; i < this.lines.length; i++) {
			var line = this.lines[i];
			if(line.striked) {
				continue;
			}
			if((line.line_number == lineNumber) && (line.level > 0) && (line.part_code !== "")) {
				hasChild = true;
				break;
			}
		}
		return hasChild;
	}
});

Cell.Totalizer = Class.create(Cell.Base, {
});
