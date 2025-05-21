var realConsole = window.console;
var timeDiff = 0


window.console = {
	log: function(msg) {
		if(realConsole !== undefined) {
			realConsole.log(msg);
		}
	}
};


Cell.Sale.prototype.checkVoided = function() {
    /* check for voided and update class */
    if(this.getState() === "VOIDED") {
        this.removeOldThresholdClasses();
        /* remove held if voided */
        if(this.getContainer().hasClassName('saleCellHeld')) {
            this.getContainer().removeClassName('saleCellHeld');
        }
        /* add cell void class */
        this.getContainer().addClassName('saleCellVoided');
    }
    else {
        this.getContainer().removeClassName('saleCellVoided');
    }
    this._contdCell.each(function(cell) {
        cell.value.checkVoided();
    });
};


Cell.Sale.prototype.checkRecall = function() {
    /* check for voided and update class */
    if(this.recalled === true) {
        this.removeOldThresholdClasses();
        if(this.getContainer().hasClassName('saleCellHeld')) {
            this.getContainer().removeClassName('saleCellHeld');
        }
        this.getContainer().addClassName('saleCellRecalled');
    }
    else {
        this.getContainer().removeClassName('saleCellRecalled');
    }
    this._contdCell.each(function(cell) {
        cell.value.checkRecall();
    });
};


Cell.Sale.prototype.updateSale = function(xml) {
  if(xml == null) {
    this._footer.update("&nbsp;");
    return;
  }
  /* get <ProductionOrder> node */
  var ponode = firstChildElement(xml);
  if(!ponode) {
    return;
  }
  var type = ponode.getAttribute("order_type") || "";
  if(type != "SALE") {
    return;
  }

  var recalled = ponode.getAttribute("recalled");
  if (recalled !== null && recalled === "True") {
    this.recalled = true;
  } else {
    this.recalled = false;
  }

  this.setOrderId(String(ponode.getAttribute("order_id") || -1));
  this.setState(String(ponode.getAttribute("state") || "&nbsp;"));
  this.setProductionState(String(ponode.getAttribute("prod_state") || ""));
  this.major = parseInt(ponode.getAttribute("major") || -1);
  this.minor = parseInt(ponode.getAttribute("minor") || -1);
  this.pod = String(ponode.getAttribute("pod_type") || "");
  this.saleType = String(ponode.getAttribute("sale_type") || "");
  this.imageMd5 = String(ponode.getAttribute("image_md5") || "");
  this.totalAmount  = Number(ponode.getAttribute("total_gross") || 0);
  this.taxAmount = Number(ponode.getAttribute("tax_total") || 0);
  this.posId = parseInt(ponode.getAttribute("pos_id") || 0);
  this.multiorderFlag = (String(ponode.getAttribute("multiorder_flag")).toLowerCase() == "true");
  this.buzzFlag = (String(ponode.getAttribute("buzz_flag")).toLowerCase() == "true");
  this.showTimer = (String(ponode.getAttribute("show_timer")).toLowerCase() == "true");
  this.properties = ponode.getElementsByTagName("Property");
  this.custom = ponode.getElementsByTagName("Custom") || [];
  this.origin = this.getOrderProperty("ORIGIN");
  this.sessionId = String(ponode.getAttribute("session_id") || "");
  this.operatorName = "";
  // "operator_id" is always 0, grab current operatior from session id
  var params = this.sessionId.split(",");
  var i;
  for(i = 0; i < params.length; i++) {
    var p = params[i].split("=");
    if (p.length > 1 && p[0] == "user") {
      this.operatorName = p[1];
      break;
    }
  }
  this.taggedLines = [];
  var taggedLines = String(ponode.getAttribute("tagged_lines") || "").split(",");
  for(i = 0; i < taggedLines.length; i++) {
    this.taggedLines.push(parseInt(taggedLines[i]));
  }
  // in JIT, side and line are by part code
  this.side = "";
  this.line = "";
  for(i = 0; i < this.custom.length; i++) {
    var custom = this.custom[i];
    var k = custom.getAttribute("key");
    if (k.startsWith("side_")) {
      this.side = custom.getAttribute("value");
    }
    if (k.startsWith("line_")) {
      this.line = custom.getAttribute("value");
    }
    if (this.side !== "" && this.line !== "") {
      // we have one side and line, assume that other products will have the same value
      break;
    }
  }
  /* remove and update classes */
  var cont = this.getContainer();
  $w(cont.className).each(function(clazzName) {
    if((clazzName.lastIndexOf("st_", 0) === 0) ||
       (clazzName.lastIndexOf("pod_", 0) === 0) ||
       (clazzName.lastIndexOf("origin_", 0) === 0)) {
      cont.removeClassName(clazzName);
    }
  });
  cont.addClassName("st_" + this.saleType);
  cont.addClassName("pod_" + this.pod);
  cont.addClassName("origin_" + this.origin);
  /* update creation date */
  this.updateCreationDate(ponode);
  this.setDisplayOrder(String(ponode.getAttribute("prod_sequence")));
  //alert(this.XMLtoString(xml));
  this.lines.clear();
  if (_main.showCellItems == true) {
    this.addItemsRecursively(xml.getElementsByTagName('Items')[0], 0, null);
  }
  if (_main.enableTagging && this.selectedLine === 0) {
    // select first time by default
    this.selectNextLine();
  }
  this.updateFooter();
  this.redrawItems();
  this.checkColors();
  if(_main.simulateBuzzer && this.buzzFlag) {
    _main.playSound(_main.soundFile);
  }
  if (custom && custom.updateSale) {
    custom.updateSale(this);
  }
};


Cell.Sale.prototype.hideIconRight = function() {
    if(!this._showContRight && !this._showMoreIcon) {
        var icon = $(this._cellId + "_header_contd_right");
        icon.removeClassName("continuedRight moreOrders");
        icon.hide();
    } else {
        this.showIconRight();
	}
};


_main.bindModelTagHooks = function() {
    h = _main.modelTagHooks;
    h.set("ViewUpdate", function(node) {
        /* get ProductionOrder node */
        var ponode = firstChildElement(node);
        if(!ponode) {
            return;
        }
        var cellUpdated = null;	/* save cell updated for refresh */
        var dontRefresh = false;
        /* get order id */
        var id = ponode.getAttribute("order_id") || -1;
        if(id !== -1) {
            var found = false;
            var orderDiscarded = _main.discardOrder(ponode);
            if(orderDiscarded == true) {
                // Cleanup unnecessary data from this order, since it has been served
                delete _main.orderImages[id];
            }
            /* find an existing cell displaying this order, if any */
            _main.cells.each(function(cell, idx) {
                var orderId = cell.getOrderId();
                if(orderId === id) {
                    if ((ponode.getAttribute("state") === "VOIDED" || ponode.getAttribute("state") === "ABANDONED") &&
                        _main.showVoidOrders === false && cell.isVisible() === false) {
                        //voided or abandoned orders can only be discarded if they are not being displayed}
                        //orderDiscarded = true;
                    }
                    found = true;
                    if(orderDiscarded == true) {
                        var cellFocused = _main.getFocusedCell();
                        /* remove this cell from the list of "active" cells */
                        _main.cells.splice(idx, 1);
                        cell.bump(function() {
                            if (_main.visibleCells === 1) {
                                //nothing left in this page, let's go back to the beginning
                                _main.cellIndex = 0;
                            }
                            _main.tryToSetFocus(cellFocused);
                            _main.adjustFocus(true);
                            _main.sortCells();
                            _main.freeCells.push(cell);
                        });
                        dontRefresh = true;
                        throw $break;
                    }
                    cell.updateSale(node);
                    cellUpdated = cell;
                    throw $break;
                }
            });
            if(!found) {
                if(orderDiscarded == true) {
                    return;
                }

                if(_main.freeCells.length === 0) {
                    /* add a new cell */
                    cellUpdated = new Cell.Sale(node);
                    cellUpdated.selectedLine = 0;
                    cellUpdated.setOrderId(id);
                    cellUpdated.setThresholds(_main.thresholds);
                    cellUpdated.setEffects(_main.effects);
                    cellUpdated.checkColors();
                    cellUpdated.setClickListener(_main.onCellClick);
                    cellUpdated.setDoubleClickListener(_main.onCellDoubleClick);
                    cellUpdated.setStartDragListener(_main.onStartDrag);
                    cellUpdated.setEndDragListener(_main.onEndDrag);
                    cellUpdated.setRevertDragListener(_main.onRevertDrag);
                } else {
                    /* update existing free cell */
                    cellUpdated = _main.freeCells.pop();
                    cellUpdated.selectedLine = 0;
                    cellUpdated.updateSale(node);
                    cellUpdated.updateTime();
                }
                /* add this cell to the list of "active" cells */
                _main.cells.push(cellUpdated);
            }
        }
        if(dontRefresh) {
            /* special case when a Served order arrives (we already call sortCells after bumping the order) */
            return;
        }
        /* refresh KDS */
        _main.sortCells();
    });
    h.set("Language", function(node) {
        _main.language = String(node.getAttribute("name") || "en");
        sendGetI18nMessage(function(req) {
            if(!_ajaxOk(req)) {
                _main.reload.delay(7.5);
                return;
            }
            try {
                /* jshint ignore:start */
                _main.i18nTable = eval("("+req.responseText+")");
                /* jshint ignore:end */
                /* update things that uses I18N */
                _main.cells.each(function(cell) {
                    cell.updateFooter();
                });
                _main.updateHoldDroppableText();
                L10N._reloadRules();
            } catch(ex) {
                notifyException(ex);
                _main.reload();
            }
        });
    });
    h.set("Title", function(node) {
        _main.title = String(node.getAttribute("desc") || "");
    });
    h.set("CellFormat", function(node) {
        var header = node.getAttribute("header");
        var footer = node.getAttribute("footer");
        var showItems = node.getAttribute("showItems");
        var showvoid = node.getAttribute("showVoidOrders");
        if (header) _main.cellHeaderFmt = header;
        if (footer) _main.cellFooterFmt = footer;
        if (showItems) _main.showCellItems = (showItems == "true");
        if (showvoid) _main.showVoidOrders = (showvoid == "true");
    });
    h.set("Effects", function(node) {
        _main.effects = String(node.getAttribute("state") || "on");
    });
    h.set("Layout", function(node) {
        var rows = node.getAttribute("rows") || 2;
        var cols = node.getAttribute("cols") || 8;
        _main.model.set("ROWS", rows);
        _main.model.set("COLS", cols);
        _main.model.set("HOLD", node.getAttribute("hold") || -1);
        _main.model.set("TOTAL", node.getAttribute("total") || -1);
        _main.model.set("LINES", node.getAttribute("lines") || 19);
        _main.model.set("FONTSIZE", node.getAttribute("fontsize") || -1);
        _main.model.set("IMAGELINES", parseInt(node.getAttribute("imageLines") || 0));
        _main.screenCellLimit = parseInt(rows) * parseInt(cols);
        _main.sortCells();
    });
    h.set("Printer", function(node) {
        _main.model.set("PRINTER", node.getAttribute("id"));
        _main.model.set("REPORT", node.getAttribute("report"));
        _main.sortCells();
    });
    h.set("Command", function(node) {
        var cmd = String(node.getAttribute("name") || "").toLowerCase();
        var cell;
        /* bump focused item */
        if(cmd == "bump") {
            cell = _main.getFocusedCell();
            if(cell) {
                sendSetStateMessage(cell.getOrderId(), "SERVED");
            }
            return;
        }
        /* bump specific index */
        if(cmd.indexOf("bump") === 0 || cmd.indexOf('itemsdone') === 0 || cmd.indexOf('itemsserved') === 0) {
            // replace of parseInt(cmd.substr(4))
            var idx = parseInt(cmd.split(/(\d+)/)[1]) || 0;
            if(idx > 0) {
                idx--;	/* convert cell position to index */
                cmd = cmd.split(/(\d+)/)[0]
            }
            cell = _main.getVisibleCell(idx);
            if(cell) {
				switch(cmd) {
					case 'bump':
						sendSetStateMessage(cell.getOrderId(), "SERVED");
						break;
					case 'itemsdone':
						sendSetStateMessage(cell.getOrderId(), "ITEMS_DONE");
						break;
					case 'itemsserved':
						sendSetStateMessage(cell.getOrderId(), "ITEMS_SERVED");
						break;
				}
            }
            return;
        }
        if (cmd === "masterbump") {
            cell = _main.getFocusedCell();
            if(cell !== null) {
                sendGlobalServeMessage(cell.getOrderId());
            }
            return;
        }
        switch(cmd) {
            case "refreshscreen":
                _main.reload.delay(0.5);
            break;
            case "navigatenext":
                _main.focus++;
                _main.adjustFocus(false);
                _main.refreshFocus();
                break;
            case "navigateprevious":
                _main.focus--;
                _main.adjustFocus(false);
                _main.refreshFocus();
                break;
            case "navigateup":
                cell = _main.getFocusedCell();
                if(cell) {
                    cell.selectPreviousLine();
                    cell.redrawItems();
                }
                break;
            case "navigatedown":
                cell = _main.getFocusedCell();
                if(cell) {
                    cell.selectNextLine();
                    cell.redrawItems();
                }
                break;
            case "hold":
                cell = _main.getFocusedCell();
                if(cell) {
                    sendSetStateMessage(cell.getOrderId(), (cell.getProductionState() == "HELD") ? "NORMAL" : "HELD");
                }
                break;
            case "undo":
            case "recall":
                sendUndoServeMessage();
                break;
            case "print":
                cell = _main.getFocusedCell();
                if (cell !== null) {
                    cell.printOrder();
                }
                break;
            case "selectid":
                if(!_main.selectableIds || !_main.selectableIds.length) {
                    break;
                }
                var nextId = _main.selectableIds[0];
                if(!_main.switchKdsTimeout) {
                    // no dialog opened yet, set current KDS as selected
                    nextId = _main.replacementId || _main.kdsId;
                } else {
                    // dialog is currently opened, select next KDS in list
                    for(var i=1; i < _main.selectableIds.length; i++) {
                        if(_main.selectableIds[i - 1] == _main.switchKdsCurrent) {
                            nextId = _main.selectableIds[i];
                            break;
                        }
                    }
                }
                _main.switchKdsCurrent = nextId;
                _main.showKdsSwitchScreen();
                break;
            case "changeid":
                sendChangeViewMessage(_main.switchKdsCurrent, function() {
                    window.location.reload();
                });
                break;
            case "tag":
                cell = _main.getFocusedCell();
                if(cell && !cell.lineHasChild(cell.selectedLine)) {
                    cell.selectNextLine();
                    sendToggleTagLine(cell.getOrderId(), cell.selectedLine);
                }
                break;
            case "tagmod":
                cell = _main.getFocusedCell();
                if(cell && cell.lineHasChild(cell.selectedLine)) {
                    cell.selectNextLine();
                    sendToggleTagLine(cell.getOrderId(), cell.selectedLine);
                }
                break;
        }
    });
    h.set("Thresholds", function(node) {
        var thresholds = node.getElementsByTagName('Threshold');
        for(var i = 0; i < thresholds.length; i++) {
            var id = parseInt(thresholds[i].getAttribute("id")) || -1;
            if((id == -1) || (isNaN(id))) {
                continue;
            }
            var value = parseInt(thresholds[i].getAttribute("value")) || -1;
            if((value <= 0) || (isNaN(value))) {
                continue;
            }
            _main.thresholds.set(id, value);
        }
    });
    h.set("RefreshEnd", function(node) {
        _main.focus = 0;
        _main.keepFocus = true;
        _main.sortCells();
    });
    h.set("BumpBars", function(node) {
        var simulateBumpBar = node.getAttribute("simulate") == "true";
        var bbs = node.getElementsByTagName("BumpBar");
        var len = bbs.length;
        for(var i = 0; i < len; i++) {
            var bb = bbs[i];
            var bbname = bb.getAttribute("name") || "";
            if(simulateBumpBar) {
                _main.simulateBumpBarName = bbname;
                if(!_main.simulateBumpBar) {
                    _main.startSimulateBumpbar();
                }
            } else {
                _main.simulateBumpBarName = null;
            }
            var cmds = bb.getElementsByTagName("Command");
            var cmdslen = cmds.length;
            for(var j = 0; j < cmdslen; j++) {
                var cmd = cmds[j];
                var cmdname = cmd.getAttribute("name") || "";
                cmdname = cmdname.toLowerCase();
                if(cmdname == "zoom" || cmdname == "zoomnext") {
                    var value = (cmd.getAttribute("value") || "").split(/[.|\/\\]/);
                    if(value) {
                        _main.zoomBumpBarName = bbname;
                        _main.zoomBumpBarCode = parseInt(value[0]) || 0;
                        break;
                    }
                }
            }
        }
    });
    h.set("Buzzers", function(node) {
        _main.simulateBuzzer = (node.getAttribute("simulate") == "true");
        var buzzs = node.getElementsByTagName("Buzzer");
        var len = buzzs.length;
        for(var i = 0; i < len; i++) {
            var buzz = buzzs[i];
            var params = buzz.getElementsByTagName("Parameter");
            var paramslen = params.length;
            for(var j = 0; j < paramslen; j++) {
                var param = params[j];
                var paramname = (param.getAttribute("name") || "").toLowerCase();
                if(paramname == "soundfile") {
                    var value = param.getAttribute("value") || "alert1.wav";
                    if(value) {
                        _main.soundFile = value;
                        break;
                    }
                }
            }
        }
    });
    h.set("ReplacementId", function(node) {
        _main.replacementId = node.getAttribute("id") || null;
    });
    h.set("SelectableIds", function(node) {
        var newSelectableIds = [];
        var currentSelectableIds = (node.getAttribute("value") || "").split(/[.|\/\\]/);
        for (var i = 0; i < currentSelectableIds.length; i++) {
            var el = currentSelectableIds[i];
            if (el.length !== 0) {
              newSelectableIds.push(el);
            }
        }
        _main.selectableIds = newSelectableIds;
    });
    h.set("KDSs", function(node) {
        var kdss = node.getElementsByTagName("KDS");
        for(var i = 0; i < kdss.length; i++) {
            var id = kdss[i].getAttribute("id");
            var desc = kdss[i].getAttribute("desc");
            if (id && desc) {
                _main.kdsTitles[id] = "KDS" + id + " - " + desc;
            }
        }
    });
    h.set("EnableTagging", function(node) {
        _main.enableTagging = (node.getAttribute("value") || "false") === "true";
    });
};


_main.onCellDoubleClick = function(cell) {
	// Left blank because CellDoubleClick is not available and now we want other actions other than SERVED
}


_main.discardOrder = function(order) {
    var state = order.getAttribute("prod_state") || "";
    return state == "INVALID";
};


_main.startSimulateBumpbar = function() {
    _main.simulateBumpBar = true;
    _main.BumpCount = {};
    _main.lastBump = {};

    Event.observe(window, "keydown", function(evt) {
        var code = evt.which || evt.keyCode;
        if (code && _main.simulateBumpBarName) {
            if (typeof(_main.lastBump[code]) === 'undefined') _main.lastBump[code] = new Date();
            var tempDate = _main.lastBump[code];
            _main.lastBump[code] = new Date();

            // Ignore multiples keydowns in less than 2 seconds
            if ( (new Date() - tempDate) < 2000) {
                if (typeof(_main.BumpCount[code]) === 'undefined') _main.BumpCount[code] = 0;
                if (_main.BumpCount[code] >= 5) return;
                _main.BumpCount[code]++;
            }
            else {
                _main.BumpCount[code] = 0;
            }

            sendBumpBarEvent(_main.simulateBumpBarName, code);
        }
    });
};


startEventsThread = function(callback,conncallback,completecallback) {
	if (callback) _eventsThread.callback = callback;
	if (conncallback) _notifyConnStatus.conncallback = conncallback;
	if (completecallback) startEventsThread.completecallback = completecallback;
	var url = "/mwapp/events/start?subject=KDS"+_main.kdsId+"&_ts="+new Date().getTime();
	new Ajax.Request(url, {
		method: 'get',
		onComplete: function(res) {
			try {
			  var serverDatetime = res.getHeader('date')
        if (serverDatetime) {
          timeDiff = (new Date()).getTime() - (new Date(serverDatetime)).getTime()
        }
				_notifyConnStatus(res);
				if (res.getHeader("X-conflicted") == "true") {
					var message = I18N("$KDS_POSSIBLE_CONFLICT");
					if (message == "KDS_POSSIBLE_CONFLICT") {
						message = "A possible conflict was detected.\nPlease check if this KDS is not opened anywhere else.";
					}
					sendLogMessage("ERROR", "notifyException", message);
				} else if (_ajaxOk(res)) {
					if(startEventsThread.completecallback) {
						startEventsThread.completecallback();
					}
					_eventsThread.lastFailed = false;
					var sync = res.getHeader("X-sync-id");
					if (sync !== null) {
						_eventsThread.sync = sync;
						_eventsThread.defer();
						return;
					}
				}
			} catch (ex) {
				notifyException(ex);
			}
			/* On any failure, try again in 7.5 seconds*/
			_main.reload.delay(7.5);
		}
	});
};


_main.updateClock = function() {
    if(_main.clockId) {
        clearTimeout(_main.clockId);
        _main.clockId = null;
    }
    _main.cells.each(function(cell) {
        if (cell.visible === true) cell.updateTime();
    });

    var rows = getModelValue("ROWS");
	var cols = getModelValue("COLS");

    var dateNow = new Date();
    var correctedDate = new Date(dateNow.getTime() + timeDiff)
    var time = ("0" + correctedDate.getHours()).slice(-2) + ":" + ("0" + correctedDate.getMinutes()).slice(-2) + ":" + ("0" + correctedDate.getSeconds()).slice(-2);

    if (typeof(cols) !== 'undefined') {
        _main.statusBarText.update(((_main.title !== "") ? time + "  -  " + _main.title + " :: " : "") + "Zoom " + cols + "x" + rows + " - Pedidos: " + _main.cells.size());
    }

    _main.clockId = setTimeout(_main.updateClock, 1000);
};


_main.sortCells = function() {
	var viewport = { width: 0, height: 0 };
    var i, len;
    var rows = getModelValue("ROWS");
    var cols = getModelValue("COLS");
    var hold = parseInt(getModelValue("HOLD"));
    var lines = getModelValue("LINES");
    var fontSize = getModelValue("FONTSIZE");
    var imageLines = getModelValue("IMAGELINES");
    /* just for security */
    if(!rows || !cols || !_main.keepFocus) {
        return;
    }
    if(isNaN(hold)) {
        hold = -1;
    }
    /* remember where the focus is now */
    var cellFocused = _main.getFocusedCell();
    _main.getViewportSize(viewport);
    _main.setMainBodySize(viewport);
    /* sort cells by displayOrder */
    _main.cells.sort(_main.sortByDisplayOrder);
    /* hide cells */
    var bodyCol;
    var totalCells = _main.cells.length;
    /* stop any running effect */
    for(i = 0; i < totalCells; i++) {
        cell = _main.cells[i];
        if(cell) {
            cell.stopEffects();
            cell.hideCell();
        }
    }
    /* rearrange cells, just calculate new positions, but don't do any movement yet */
    var hgap = _main.getHGap();
    var vgap = _main.getVGap();
    var width = (viewport.width / cols) - hgap;
    var height = (viewport.height / rows) - vgap;
    var x, y, cell, top, left;
    var idx = _main.cellIndex;
    var idxHeld = 0;
    if(fontSize <= 0) {
        fontSize = (Math.floor(height / lines)) - vgap;
    }
    var rearrange = [];
    var maxBodyCols = -1;
    var itemToMove;
    var lastRow = 0;
    var lastX = 0;
    var lastY = 0;
    var lastCell = null;
    var lastCellHeld = null;
    var cellToAppendChild = null;
    /* find held cells */
    var heldZone = false;
    var heldCells = [];
    var heldSpaceReq = 0;
    for(i = (_main.cells.length - 1); i >= 0; i--) {
        cell = _main.cells[i];
        cell.setCellHints(width, height, lines, imageLines, _main.headerLines, _main.footerLines, _main.headerColumns);	/* to get cell spaces required */
        if(cell && cell.getProductionState() == "HELD") {
            cell = _main.cells.splice(i, 1)[0];
            heldSpaceReq += cell.maxBodyCols;
            heldCells.push(cell);
        }
    }
    /* move held orders to the back of the cells list in order to keep an intuitive focus */
    heldCells.reverse();
    _main.cells = _main.cells.concat(heldCells);
    /* ensure that there is at least one space reserved for held orders,
       otherwise held orders won't be restored */
    if((heldSpaceReq > 0) && (hold == -1)) {
        hold = (cols * rows);
    }
    var heldSpaces = ((cols * rows) - hold) + 1;
    if(heldSpaceReq < heldSpaces) {
        hold += (heldSpaces - heldSpaceReq);
    }
    /* make sure that the held droppable zone <div> has the correct size (half of screen) */
    if(_main.holdDroppable) {
        _main.holdDroppable.style.left = "0px";
        _main.holdDroppable.style.width = viewport.width + "px";
        _main.holdDroppable.style.height = (viewport.height / 2) + "px";
    }
    /* visibleCells is used to do the focus loop */
    _main.visibleCells = 0;
    /* start calculating cell positions */
    for(y = 0; y < rows; y++) {
        for(x = 0; x < cols; x++) {
            /* heldZone will be true when we are over a space reserved for held orders */
            heldZone = (hold != -1) && ((((y * cols) + x) + 1) >= hold);
            /* maxBodyCols contains the remaining number of columns to be displayed for last cell drawn (first time is -1) */
            if(maxBodyCols <= 0) {
                /* get next cell to display */
                if(!heldZone) {
                    cell = _main.cells[idx];
                    /* skip cells in HELD state */
                    while(cell && cell.getProductionState() == "HELD") {
                        idx++;
                        cell = _main.cells[idx];
                    }
                } else {
                    cell = heldCells[idxHeld];
                }
                if(cell) {
                    /* valid cell found */
                    cellToAppendChild = cell;
                    cell.setCellHints(width, height, lines, imageLines, _main.headerLines, _main.footerLines, _main.headerColumns);	/* required to draw items with the correct dimensions */
                    cell.redrawItems();
                    top = (y * (height + vgap));
                    left = (x * (width + hgap));
                    itemToMove = new Array(1, cell, left, top, width, height);
                    rearrange.push(itemToMove);
                    /* body cols were already calculated by setCellHints */
                    maxBodyCols = cell.maxBodyCols;
                    lastRow = -1;
                    lastY = -1;
                    lastX = 0;
                    if(!heldZone) {
                        idx++;
                    } else {
                        idxHeld++;
                    }
                    _main.visibleCells++;
                }
            }
            if(cell) {
                len = rearrange.length;
                if(y == lastRow) {
                    /* container is the original cell expanded, find it in our rearrange array and update size */
                    for(i = 0; i < len; i++) {
                        itemToMove = rearrange[i];
                        if(itemToMove[1] == cellToAppendChild) {
                            /* update size */
                            itemToMove[4] += (width + hgap);
                            itemToMove[5] = height;
                            cellToAppendChild.hideContdRight();
                        }
                    }
                    lastX++;
                } else {
                    lastY++;
                    /* container is another cell, because the order continues in a new row */
                    cellToAppendChild = cell.getCellByRow(lastY);	/* this will create the new cell if necessary */
                    top = (y * (height + vgap));
                    left = (x * (width + hgap));
                    itemToMove = new Array(1, cellToAppendChild, left, top, width, height);
                    rearrange.push(itemToMove);
                    lastRow = y;
                    lastX = 0;
                    if(lastY > 0) {
                        if(_main.headerColumns < 0) {
                            cellToAppendChild.showContdLeft();
                        }
                        cell.getCellByRow(lastY - 1).showContdRight();
                    } else if(lastY === 0) {
                        cell.hideContdLeft();
                        cell.hideContdRight();
                        cell.hideMoreLabel();
                        cell.clearClippedCells();
                    }
                }
                /* rearrange cell column */
                bodyCol = cell.getBodyColumn(cell.maxBodyCols - maxBodyCols);
                if(bodyCol) {
                    /* reparent since the column may belong to another cell now */
                    bodyCol = bodyCol.remove();
                    cellToAppendChild.getContainer().insert({ top: bodyCol });
                    itemToMove = new Array(2, bodyCol, (lastX * (width + hgap)), cell.lineHeight * cell.getHeaderLines(cell.maxBodyCols - maxBodyCols), width, cell.bodyHeight);
                    rearrange.push(itemToMove);
                }
            }
            maxBodyCols--;
            /* force to cut last order here if the next cell is in held zone, or is the last cell space */
            var nextIsHeldZone = (hold != -1) && ((((y * cols) + x) + 2) >= hold);
            var isLastCell = (x == (cols - 1)) && (y == (rows - 1));
            if((((nextIsHeldZone) && (idxHeld === 0)) || (isLastCell)) && (maxBodyCols > 0)) {
                if(cellToAppendChild && _main.footerLines > 0) {
                    cellToAppendChild.showMoreLabel();
                    if (isLastCell) {
                        cellToAppendChild.markClippedCells(cell.maxBodyCols - maxBodyCols);
                    }
                }
                if(cell) {
                    /* hide unused colums for last cell */
                    while(maxBodyCols > 0) {
                        bodyCol = cell.getBodyColumn(cell.maxBodyCols - maxBodyCols);
                        if(bodyCol) {
                            bodyCol.hide();
                        }
                        maxBodyCols--;
                    }
                }
                maxBodyCols = 0;
            } else if(!maxBodyCols && cell && cellToAppendChild) {
                /* if the maximum number of columns to display is limited (and this limit is reached), show "MORE..." label */
                if(cell.maxBodyCols < cell.colSpan && _main.footerLines > 0) {
                    cellToAppendChild.showMoreLabel();
                    if (isLastCell) {
                        cellToAppendChild.markClippedCells(cell.maxBodyCols - maxBodyCols);
                    }
                } else {
                    cellToAppendChild.hideMoreLabel();
                    cellToAppendChild.clearClippedCells();
                }
            }
            /* store the last cell displayed, for regular orders and held orders
               this is used later to hide remaining cells */
            if(!heldZone) {
                lastCell = cellToAppendChild;
            } else {
                lastCellHeld = cellToAppendChild;
            }
        }
    }
    /* hide continuation icons if the last cell fits in a single row (non line-breaking cell) */
    if(cell && cellToAppendChild && (cellToAppendChild == cell)) {
        cell.hideContdLeft();
        cell.hideContdRight();
    }
    /* now start moving cells around, show and hide as necessary */
    len = rearrange.length;
    for(i = 0; i < len; i++) {
        itemToMove = rearrange[i];
        if(itemToMove[0] == 1) {
            cell = itemToMove[1];
            cell.hideMoreIcon();
            cell.resize(itemToMove[4], itemToMove[5]);
            cell.move(itemToMove[2], itemToMove[3]);
            cell.setFontSize(fontSize);
            cell.show();
        } else {
            /* column body does not need effects, just rearrange */
            bodyCol = itemToMove[1];
            bodyCol.style.position = "absolute";
            bodyCol.style.width = (itemToMove[4]) + 'px';
            bodyCol.style.height = itemToMove[5] + 'px';
            bodyCol.style.left = itemToMove[2] + 'px';
            bodyCol.style.top = itemToMove[3] + 'px';
            bodyCol.style.fontSize = fontSize + 'px';
            bodyCol.show();
        }
    }
    var hideContdCell = function(contdCell) {
        var found = false;
        if(contdCell.value && contdCell.value.getContainer()) {
            for(var k = 0; k < contdCell.value.getContainer().childElements().length; k++) {
                var subDiv = contdCell.value.getContainer().childElements()[k];
                if((subDiv.identify().indexOf("_body_") != -1) && (subDiv.visible())) {
                    found = true;
                }
            }
            if(!found) {
                contdCell.value.hide();
            }
        }
    };
    /* hide unused continuations */
    for(i = 0; i < totalCells; i++) {
        cell = _main.cells[i];
        if(cell && cell._contdCell) {
            cell._contdCell.each(hideContdCell);
        }
    }
    /* hide unused cells */
    var hideCell = function(inner_cell) {
        inner_cell.value.hide();
    };
    var first = true;
    for(i = idx; i < totalCells; i++) {
        cell = _main.cells[i];
        if(cell && (cell.getProductionState() != "HELD")) {
            if(first) {
                lastCell.showMoreIcon();
                first = false;
            }
            cell._contdCell.each(hideCell);
            cell.hide();
        }
    }
    /* hide unused held cells */
    first = true;
    len = heldCells.length;
    for(i = idxHeld; i < len; i++) {
        cell = heldCells[i];
        if(cell) {
            if(first) {
                if (lastCellHeld) lastCellHeld.showMoreIcon();
                first = false;
            }
            cell._contdCell.each(hideCell);
            cell.hide();
        }
    }
    /* try to find previously focused cell in the new arrangement */
    _main.tryToSetFocus(cellFocused);
    /* make sure that is a valid focus */
    _main.adjustFocus(true);
    _main.refreshFocus();

    var dateNow = new Date();
    var correctedDate = new Date(dateNow.getTime() + timeDiff)
    var time = ("0" + correctedDate.getHours()).slice(-2) + ":" + ("0" + correctedDate.getMinutes()).slice(-2) + ":" + ("0" + correctedDate.getSeconds()).slice(-2);

    if (typeof(cols) !== 'undefined') {
        _main.statusBarText.update(((_main.title !== "") ? time + "  -  " + _main.title + " :: " : "") + "Zoom " + cols + "x" + rows + " - Pedidos: " + _main.cells.size());
    }
};


Cell.Sale.prototype.getCellByRow = function(row) {
    if(row == 0) {
        return(this);
    }
    var cell = this._contdCell.get(row);
    if(cell == null) {
        /* create new continuation cell */
        cell = new Cell.Sale(null);
        /* copy properties */
        cell.setEffects(this.effectState);
        cell.creationDate = this.creationDate;
        cell.recalled = this.recalled;
        cell.setState(this.getState());
        cell.setProductionState(this.getProductionState());
        cell.setThresholds(this.thresholds);
        cell.setClickListener(this.onClickCallback);
        cell.setDoubleClickListener(this.onDoubleClickCallback);
        cell.setStartDragListener(this.onStartDrag);
        cell.setEndDragListener(this.onEndDrag);
        cell.setRevertDragListener(this.onRevertDrag);
        cell.setOrderId(this.getOrderId());
        cell.checkColors();
        /* hide header and footer if necessary */
        var footerLines = this.footerLines;
        var headerColumns = this.headerColumns;
        if(headerColumns > 0) {
            cell._header_table.style.display = "none";
        }
        if (!footerLines) {
            cell._footer_table.style.height = "0px";
        }
        /* add to hash table */
        this._contdCell.set(row, cell);
    }
		return(cell);
};


Cell.Sale.prototype.addItemsRecursively = function(node, level, parentQty, parentType, parentDefaultQty) {
    if(typeof(parentType) === "undefined") {
        parentType = "COMBO";
    }

    if(typeof(parentDefaultQty) === "undefined") {
        parentDefaultQty = 1;
    }

    var items = node.childNodes;
    if(items) {
        var len = items.length;
        var indentstr = "";
        for(var i = 0; i < len; i++) {
            var item = items[i];
            if(!isElement(item) || (item.tagName != "Item")) {
                continue;
            }
            var qty = parseInt(item.getAttribute("qty") || 0);
            var type = String(item.getAttribute("item_type"));
            var striked = (parentQty==0) || (qty == 0);
            var only = (item.getAttribute("only") == "true" && (type == "CANADD" || type == "INGREDIENT"));
            var defaultQty = item.getAttribute("default_qty");
            var defQty = (item.getAttribute("qty") == item.getAttribute("default_qty"));
            var added = (type == "CANADD" && qty > 0) || (type == "INGREDIENT" && defQty == false && qty > 0)
            indentstr = "";
            /* add item */
            for(let indent = 0; indent < level; indent++) {
                indentstr += "&nbsp;&nbsp;&nbsp;";
            }
            var desc = String(item.getAttribute("description") || "");
            var hasLabel = item.getAttribute("modifier_label") != null;
            var modStr = String((item.getAttribute("modifier_label")) ? item.getAttribute("modifier_label") + "&nbsp;" : "");
            var onlyStr = String((only) ? I18N("$ONLY") + "&nbsp;" : "");
            var qtyStr = String(hasLabel || level != 0 ? "" : qty + "&nbsp;&nbsp;");
            /* avoid displaying "With" with only */

            var repeat = 1;
            if (parentType != "COMBO") {
                if ( (type == "CANADD" || type == "INGREDIENT") ) {
                    if (qty == defaultQty) {
                        repeat = 0;
                    }
                    else
                    {
                        if (qty < defaultQty) {
                            qtyStr = "Sem&nbsp;&nbsp;&nbsp;"
                        }

                        if (qty > defaultQty) {
                            qtyStr = "Extra&nbsp;";
                            repeat = qty - defaultQty;
                        }
                    }
                }
            }

            if(only && (modStr != "") && defQty) modStr = "";
            if (item.getAttribute("json_tags") && item.getAttribute("json_tags").indexOf("CFH=true") < 0) {
                for (var j = 0; j < repeat; j++) {
		            this.lines.push({
		                "line": indentstr + qtyStr + onlyStr + modStr + desc,
		                "striked": striked,
		                "added": added,
		                "line_number": parseInt(item.getAttribute("line_number")),
		                "level": parseInt(item.getAttribute("level")),
		                "part_code": parseInt(item.getAttribute("part_code"))
		            });
                }
            }
            /* add sub items */
            this.addItemsRecursively(item, level + 1, (level == 0) ? qty : parentQty, type, defaultQty);
        }
    }
};


Cell.Sale.prototype.updateCreationDate = function(ponode) {
    var date = String(ponode.getAttribute("display_time"));
    if(date) {
        var tempTime = new Date();
        tempTime.setISO8601(date);
        this.creationDate = new Date(tempTime.getTime() + timeDiff);
    }
};


Cell.Sale.prototype.parseCustomFunction = function(template) {
    var re = /#\{function:(.*?)\}/g;
    re.lastIndex = 0;
    var match = re.exec(template);
    if (match) {
        // get function by string
        var scope = window;
        var scopeSplit = match[1].split('.');
        for (var i = 0; i < scopeSplit.length - 1; i++) {
            scope = scope[scopeSplit[i]];
            if (scope === undefined) {
                return null;
            }
        }
        var fn = scope[scopeSplit[scopeSplit.length - 1]];
        if(typeof fn === 'function') {
            return fn;
        }
    }
    return null;
}


_main.showWarningScreen = true;


window.formatFooter = function(cell, footer) {
    try {
        var isPriority = false;
        var customerName = "";
        var orderId = (cell.orderId % 1000).padLeft(3, "0")
        for (var i = 0; i < cell.properties.length; i++) {
            var key = cell.properties.item(i).attributes.key.value;
            var value = cell.properties.item(i).attributes.value.value;
            if (key === 'PRIORITY') {
                isPriority = value === 'true';
            }
            if (key === 'CUSTOMER_NAME') {
                customerName = value;
                break;
            }
        }

        var cellState = '(' + cell.state[0] + ') - ' ;

        footer.update(
          cellState + (isPriority ? I18N("$PRIORITY").toUpperCase() + '</br>' : '') + orderId + (customerName ? " - " + customerName : "")
        );
    } catch (e) {
        footer.update(e.toString());
    }
};


Number.prototype.padLeft = function (n,str){
    return Array(n-String(this).length+1).join(str||'0')+this;
}
