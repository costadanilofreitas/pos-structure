import React, { Component } from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'
import injectSheet from 'react-jss'

import { ensureArray } from '3s-posui/utils'
import { ScrollPanel } from '3s-widgets'
import { I18N } from '3s-posui/core'

import SalePanelItem from './item'
import SalePanelItemOptions from './item-options'

import { deepEquals } from '../../../../util/renderUtil'


const styles = {
  salePanelItemsRoot: {
    composes: 'sale-panel-items-root',
    position: 'absolute',
    height: '100%',
    width: '100%'
  },
  salePanelItemsRefund: {
    composes: 'sale-panel-items-refund',
    '& *': {
      backgroundColor: '#f9f4de'
    }
  },
  salePanelItemsVoided: {
    composes: 'sale-panel-items-voided',
    '& *': {
      color: '#bb0000 !important',
      textDecoration: 'line-through'
    }
  },
  salePanelItemsTrainingMode: {
    composes: 'sale-panel-items-training-mode',
    '& *': {
      backgroundColor: '#ffdfdf'
    }
  },
  emptyCartMessageContainer: {
    fontSize: '3vmin',
    height: '100%',
    display: 'flex',
    alignItems: 'center',
    textAlign: 'center'
  }
}

class SalePanelItems extends Component {
  makeVisible = null
  makeVisibleLast = null
  makeVisibleFirst = null
  makeVisibleCurrent = null
  scrollPanel = null
  saleLines = null

  renderSaleLines() {
    const {
      order, selectedLine, showNotRequiredOptions, currencySymbol, currencySymbolNegative, showArrowOnSelection,
      onLineClicked, selectedParent, onLineRendered, onOptionRendered, onModifierRendered, onItemRendered, biggerFont,
      onCommentRendered, modQtyPrefixes, modCommentPrefixes, hideQtyOneTopLevel, hideQtyOneLowLevel, showPricedOptions,
      l10n, showHoldAndFire, showSaleItemOptions, showCoupons, ignorePLUs, showDiscountedPrice, classes, changeQuantity,
      deleteLines, onShowModifierScreen, onUnselectLine, showSeatInSalePanelLine
    } = this.props
    const attributes = order['@attributes'] || {}
    const isRefund = attributes.type === 'REFUND'
    let lastSelectedParent = {}
    let lastOption = null
    let lastOptionChild = null
    let lastProduct = null
    const hiddenLines = {}
    this.saleLines = this.getSaleLines(order, attributes)
    const voidedLines = this.getVoidedLines(this.saleLines)

    return this.saleLines.map((item, index) => {
      const saleLine = (item || {})['@attributes'] || {}
      const lineNumber = saleLine.lineNumber
      const nextSaleLine = (this.saleLines[index + 1] || {})['@attributes'] || {}
      const nextLineNumber = nextSaleLine.lineNumber
      const isLastLine = lineNumber !== nextLineNumber
      const qty = Number(saleLine.qty) || Number(0)
      const chosenQty = Number(saleLine.chosenQty) || Number(0)
      const level = parseInt(saleLine.level, 10) || 0
      const isOption = saleLine.itemType === 'OPTION'
      const isProduct = saleLine.itemType === 'PRODUCT'
      const isIngredient = saleLine.itemType === 'INGREDIENT'
      const isCoupon = saleLine.itemType === 'COUPON'
      const isIngredientOrOption = isOption || isIngredient
      let showItem = true

      if (_.includes(ignorePLUs, saleLine.partCode)) {
        return null
      }
      if (!showCoupons && isCoupon) {
        return null
      }

      const fullCode = `${saleLine.itemId}.${saleLine.partCode}`
      const lineLevelAndCode = `${lineNumber}-${level}-${fullCode}`
      if (_.includes(voidedLines, lineLevelAndCode)) {
        return null
      }
      if (level === 0) {
        lastSelectedParent = saleLine
      }

      let ref = null
      if (this.makeVisible != null && this.isSameLine(saleLine, this.makeVisible)) {
        ref = (el) => {
          this.makeVisibleLast = el
        }
      }
      if (this.props.selectedLine != null && this.isSameLine(saleLine, this.props.selectedLine)) {
        ref = (el) => {
          this.makeVisibleCurrent = el
        }
      }
      if (selectedParent != null) {
        if (this.isSameLine(saleLine, selectedParent)) {
          ref = (el) => (this.makeVisibleFirst = el)
        }
      }

      let isOptionGrandChild = false
      if (isOption) {
        lastOption = fullCode
      } else if (saleLine.itemId === lastOption) {
        lastOptionChild = fullCode
      } else if (saleLine.itemId === lastOptionChild) {
        isOptionGrandChild = true
      }
      let isProductChild = false
      if (isProduct) {
        lastProduct = fullCode
      } else if (saleLine.itemId === lastProduct) {
        isProductChild = true
      }
      if (!hiddenLines[lineNumber]) {
        hiddenLines[lineNumber] = []
      }

      hiddenLines[lineNumber] = _.filter(
        hiddenLines[lineNumber],
        (hiddenLevel) => hiddenLevel < level
      )
      const maxQty = parseInt(saleLine.maxQty, 10) || 0
      const optionPrice = parseFloat(saleLine.itemPrice || '0')
      const showOption = (showNotRequiredOptions && (chosenQty < maxQty)) ||
        (showPricedOptions && optionPrice > 0)
      const canSelectOption = isOption && (chosenQty < qty || showOption)
      if (isOption && !canSelectOption) {
        hiddenLines[lineNumber].push(level)
      }
      const hiddenAncestors = hiddenLines[lineNumber].length
      if (qty === Number(0) && (!isIngredientOrOption || (isOption && !canSelectOption))) {
        showItem = false
      }
      if (isOption && !canSelectOption) {
        showItem = false
      }

      const isSelectedLine = selectedLine && selectedLine.lineNumber === lineNumber
      const mustShowSaleItemOptions = showSaleItemOptions && isSelectedLine && isLastLine
      const parentSaleLine = this.saleLines.find(x => x.lineNumber === saleLine.lineNumber && x.level === '0')
      return (
        <div key={index} className={mustShowSaleItemOptions ? classes.totemSelectedLine : ''}>
          {showItem &&
          <SalePanelItem
            key={index}
            saleLine={item || {}}
            parentLine={
              (lastSelectedParent.lineNumber === lineNumber) ? lastSelectedParent : {}
            }
            isLastLine={isLastLine}
            isRefund={isRefund}
            isModifier={isProductChild || isOptionGrandChild}
            hiddenAncestors={hiddenAncestors}
            currencySymbol={currencySymbol}
            currencySymbolNegative={currencySymbolNegative}
            showArrowOnSelection={showArrowOnSelection}
            onLineClicked={onLineClicked}
            selectedLine={selectedLine}
            selectedParent={selectedParent}
            onLineRendered={onLineRendered}
            onOptionRendered={onOptionRendered}
            onModifierRendered={onModifierRendered}
            onItemRendered={onItemRendered}
            onCommentRendered={onCommentRendered}
            modQtyPrefixes={modQtyPrefixes}
            modCommentPrefixes={modCommentPrefixes}
            hideQtyOneTopLevel={hideQtyOneTopLevel}
            hideQtyOneLowLevel={hideQtyOneLowLevel}
            showHoldAndFire={showHoldAndFire}
            l10n={l10n}
            showDiscountedPrice={showDiscountedPrice}
            biggerFont={biggerFont}
            showSeatInSalePanelLine={showSeatInSalePanelLine}
            {...(!mustShowSaleItemOptions ? { ref } : {})}
          />}
          {mustShowSaleItemOptions &&
          <SalePanelItemOptions
            ref={ref}
            classes={classes}
            itemQuantity={parseInt((parentSaleLine || { qty: 1 }).qty, 10)}
            lineNumber={parseInt(lineNumber, 10)}
            changeQuantity={changeQuantity}
            deleteLines={deleteLines}
            showModifierScreen={onShowModifierScreen}
            onDelete={onUnselectLine}
          />}
        </div>
      )
    }, this)
  }

  renderEmptyMessage() {
    const { order, classes, showCartMessage } = this.props
    const attributes = order['@attributes'] || {}
    this.saleLines = this.getSaleLines(order, attributes)
    const voidedLines = this.getVoidedLines(this.saleLines)

    if (this.saleLines.length - voidedLines.length <= 0 && showCartMessage) {
      return (
        <div className={classes.emptyCartMessageContainer}>
          <I18N id="$EMPTY_CART_MESSAGE"/>
        </div>
      )
    }

    return null
  }

  getVoidedLines(saleLines) {
    const voidedLines = []
    let lastLevelVoided = null
    let lastLineNumberVoided = null
    saleLines.forEach((item) => {
      const saleLine = (item || {})['@attributes'] || {}
      const lineNumber = saleLine.lineNumber
      const level = parseInt(saleLine.level, 10) || 0
      const qty = Number(saleLine.qty) || Number(0)
      const isIngredientOrOption = _.includes(['OPTION', 'INGREDIENT'], saleLine.itemType)
      const fullCode = `${saleLine.itemId}.${saleLine.partCode}`
      const lineLevelAndCode = `${lineNumber}-${level}-${fullCode}`

      if (lastLevelVoided != null) {
        if (lineNumber !== lastLineNumberVoided || level <= lastLevelVoided) {
          lastLevelVoided = null
          lastLineNumberVoided = null
        } else {
          voidedLines.push(lineLevelAndCode)
        }
      }
      if (qty === Number(0) && !isIngredientOrOption && lastLevelVoided == null) {
        lastLevelVoided = level
        lastLineNumberVoided = lineNumber
        voidedLines.push(lineLevelAndCode)
      }
    })
    return voidedLines
  }

  getSaleLines(order, attributes) {
    let saleLines = ensureArray(order.SaleLine || [])
    if (!this.props.showFinishedSale && !_.includes(['IN_PROGRESS', 'TOTALED'], attributes.state)) {
      saleLines = []
    }

    saleLines = this.removeSaleLinesCFH(_.cloneDeep(saleLines))

    return saleLines
  }

  removeSaleLinesCFH(saleLines) {
    const CFHSaleLines = this.getCFHSaleLines(saleLines)
    this.fixSaleLinesLevels(CFHSaleLines, saleLines)

    return saleLines.filter(x => !CFHSaleLines.includes(x))
  }

  fixSaleLinesLevels(CFHSaleLines, saleLines) {
    for (let i = 0; i < CFHSaleLines.length; i++) {
      const itemId = `${CFHSaleLines[i]['@attributes'].itemId}.${CFHSaleLines[i]['@attributes'].partCode}`
      _.forEach(saleLines.filter(x => x['@attributes'].itemId.startsWith(itemId)), line => {
        line['@attributes'].level = (parseInt(line['@attributes'].level, 10) - 1).toString()
      })
    }
  }

  getCFHSaleLines(saleLines) {
    const CFHSaleLines = []
    for (let i = 0; i < saleLines.length; i++) {
      if (this.isCFH(saleLines[i])) {
        CFHSaleLines.push(saleLines[i])
      }
    }

    return CFHSaleLines
  }

  isCFH(saleLine) {
    if (saleLine == null) {
      return false
    }

    const { products } = this.props
    const partCode = saleLine.partCode != null ? saleLine.partCode : saleLine['@attributes'].partCode
    return products[partCode] ? products[partCode] !== undefined && products[partCode].CFH === 'true' : false
  }

  isSameLine = (line1, line2) => {
    return (line1.lineNumber === line2.lineNumber &&
      line1.itemId === line2.itemId &&
      line1.itemType === line2.itemType &&
      line1.level === line2.level &&
      line1.partCode === line2.partCode)
  }

  shouldComponentUpdate(nextProps) {
    const selectedLine = nextProps.selectedLine || {}
    const order = nextProps.order || {}

    this.makeVisible = _.findLast(order.SaleLine, (item) => {
      const saleLine = (item || {})['@attributes'] || {}
      return (saleLine.lineNumber === selectedLine.lineNumber)
    })

    let lineChanges = false
    const shouldRender = !deepEquals(this.props, nextProps, 'order', 'getMessage')
    if (this.props.order != null && nextProps.order != null && shouldRender === false) {
      const ignoredProps = ['@attributes', 'saleTypeDescr', 'lastNewLineAt', 'saleType', 'lastNewLineAtGMT']
      lineChanges = !deepEquals(this.props.order, nextProps.order, ...ignoredProps)
    }

    return shouldRender || lineChanges
  }

  componentDidUpdate() {
    if (this.scrollPanel) {
      if (this.makeVisibleFirst != null) {
        this.scrollPanel.ensureVisible(this.makeVisibleFirst)
      }
      if (this.makeVisibleLast != null) {
        this.scrollPanel.ensureVisible(this.makeVisibleLast)
      }
      if (this.makeVisibleCurrent != null) {
        this.scrollPanel.ensureVisible(this.makeVisibleCurrent)
      }

      this.makeVisible = null
      this.makeVisibleLast = null
      this.makeVisibleFirst = null
      this.makeVisibleCurrent = null
    }
  }

  render() {
    const { classes, style, order, trainingMode, styleOverflow } = this.props
    if (!order) {
      return null
    }
    const rootClasses = [classes.salePanelItemsRoot]
    const attributes = order['@attributes'] || {}
    if (attributes.type === 'REFUND') {
      rootClasses.push(classes.salePanelItemsRefund)
    }
    const finished = _.includes(['PAID', 'STORED', 'VOIDED'], attributes.state)
    if (this.props.showFinishedSale && finished) {
      rootClasses.push(classes.salePanelItemsDisabled)
      if (attributes.state === 'VOIDED') {
        rootClasses.push(classes.salePanelItemsVoided)
      }
    }
    if (trainingMode) {
      rootClasses.push(classes.salePanelItemsTrainingMode)
    }

    return (
      <div className={rootClasses.join(' ')} style={style}>
        <ScrollPanel
          key={`scroll_panel_${finished}`}
          reference={(el) => {
            this.scrollPanel = el
          }}
          styleCont={styleOverflow ? { overflowY: 'auto' } : {}}
        >
          {this.renderSaleLines()}
        </ScrollPanel>
        {this.renderEmptyMessage()}
      </div>
    )
  }
}

SalePanelItems.propTypes = {
  classes: PropTypes.object,
  currencySymbol: PropTypes.string,
  currencySymbolNegative: PropTypes.string,
  showArrowOnSelection: PropTypes.bool,
  style: PropTypes.object,
  showFinishedSale: PropTypes.bool,
  onLineClicked: PropTypes.func,
  trainingMode: PropTypes.bool,
  selectedLine: PropTypes.object,
  order: PropTypes.object,
  showNotRequiredOptions: PropTypes.bool,
  selectedParent: PropTypes.object,
  onLineRendered: PropTypes.func,
  onOptionRendered: PropTypes.func,
  onModifierRendered: PropTypes.func,
  onItemRendered: PropTypes.func,
  onCommentRendered: PropTypes.func,
  onUnselectLine: PropTypes.func,
  modQtyPrefixes: PropTypes.object,
  modCommentPrefixes: PropTypes.object,
  hideQtyOneTopLevel: PropTypes.bool,
  hideQtyOneLowLevel: PropTypes.bool,
  showPricedOptions: PropTypes.bool,
  l10n: PropTypes.object,
  showHoldAndFire: PropTypes.bool,
  showCoupons: PropTypes.bool,
  ignorePLUs: PropTypes.array,
  showDiscountedPrice: PropTypes.bool,
  changeQuantity: PropTypes.func,
  deleteLines: PropTypes.func,
  onShowModifierScreen: PropTypes.func,
  showSaleItemOptions: PropTypes.bool,
  styleOverflow: PropTypes.bool,
  biggerFont: PropTypes.bool,
  showSeatInSalePanelLine: PropTypes.bool,
  showCartMessage: PropTypes.bool,
  products: PropTypes.object
}

SalePanelItems.defaultProps = {
  style: {},
  onLineClicked: (selectedLine) => selectedLine,
  showFinishedSale: true,
  skipAutoSelect: false,
  showPricedOptions: false,
  builds: {},
  l10n: {},
  showCoupons: true,
  ignorePLUs: [],
  showCartMessage: false
}

export default injectSheet(styles)(SalePanelItems)
