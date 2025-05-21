import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { jss } from 'react-jss'

import { ensureArray, ensureDecimals } from '3s-posui/utils'
import RendererChooser from '../../../../../component/renderer-chooser'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

export default class SalePanelItem extends PureComponent {
  addComment(level, ignoreComments) {
    const { classes, saleLine, onCommentRendered } = this.props
    const comments = ensureArray((saleLine || {}).Comment || [])
    const commentClasses = [classes.salePanelItemRoot]
    const commentLevelClass = `salePanelItemCommentLevel${level}`
    if (_.has(classes, commentLevelClass)) {
      commentClasses.push(classes[commentLevelClass])
    } else {
      commentClasses.push(`sale-panel-item-comment-level${level}`)
    }
    return comments.map((comment, index) => {
      const commentAttr = (comment || {})['@attributes'] || {}
      if (_.includes(ignoreComments, commentAttr.commentId)) {
        return null
      }
      return (
        <div key={index} className={commentClasses.join(' ')}>
          {(onCommentRendered) ? onCommentRendered(comment) : commentAttr.comment}
        </div>
      )
    })
  }

  drawArrow(saleLine) {
    if (!this.props.showArrowOnSelection || saleLine !== this.props.selectedLine) {
      return null
    }
    const level = parseInt(saleLine.level, 10) || 0
    return (
      <div className="item-arrow-selection">
        <svg
          style={{ height: '100%', backgroundColor: 'transparent !important' }}
          viewBox="0 0 30 100"
          preserveAspectRatio="none"
        >
          <path
            className={`item-arrow-selection-level${level}`}
            style={{
              fillRule: 'evenodd',
              strokeWidth: '2px',
              strokeLinecap: 'butt',
              strokeLinejoin: 'miter',
              strokeOpacity: 1,
              fillOpacity: 1,
              miterLimit: 0
            }}
            d="M 0,0 30,50 0,100"
          />
        </svg>
      </div>
    )
  }

  render() {
    const {
      classes, onLineRendered, onOptionRendered, onModifierRendered, onItemRendered, isRefund,
      currencySymbol, currencySymbolNegative, parentLine, modQtyPrefixes, modCommentPrefixes,
      hideQtyOneTopLevel, hideQtyOneLowLevel, hiddenAncestors, isModifier, l10n,
      renderLinePrefix, showHoldAndFire, showDiscountedPrice, showSeatInSalePanelLine
    } = this.props
    if (!this.props.saleLine) {
      return null
    }
    const saleLine = this.props.saleLine['@attributes'] || {}
    const customProperties = saleLine.customProperties || {}
    const { seat, hold, fire, course, highPriority } = customProperties
    const dontMake = customProperties.dont_make
    const comments = ensureArray((this.props.saleLine || {}).Comment || [])
    const qty = Number(saleLine.qty) || Number(0)
    const chosenQty = Number(saleLine.chosenQty) || Number(0)
    const left = qty - chosenQty
    const currencyDecimals = l10n.CURRENCY_DECIMALS || 2
    const decimalSeparator = l10n.DECIMALS_SEPARATOR || '.'
    let level = parseInt(this.props.saleLine['@attributes'].level, 10) || 0
    if (hiddenAncestors) {
      level -= hiddenAncestors
    }

    const getQtyString = (qtyToDraw) => {
      if (qtyToDraw === Number(1) && ((hideQtyOneTopLevel && level === 0) || (hideQtyOneLowLevel && level > 0))) {
        return ''
      }
      return `${qtyToDraw} `
    }

    const defaultQty = parseInt(saleLine.defaultQty, 10) || 0
    const minQty = parseInt(saleLine.minQty, 10) || 0
    let lineDesc = ''
    const linePrefix = (renderLinePrefix) ? renderLinePrefix() : ''
    const descClasses = [classes.salePanelItemDesc]
    let separator = null
    const ignoreComments = []
    switch (saleLine.itemType) {
      case 'OPTION':
        if (onOptionRendered) {
          lineDesc = onOptionRendered(saleLine)
        } else {
          if (defaultQty > 0 || minQty > 0) {
            descClasses.push(classes.salePanelItemMandatoryOption)
          }
          if (left > 0) {
            const qtyLeft = getQtyString(left)
            lineDesc = `${qtyLeft}[${saleLine.productName}]`
          } else {
            lineDesc = `[${saleLine.productName}]`
            descClasses.push(classes.salePanelItemNotRequiredOption)
          }
          descClasses.push(classes.salePanelItemOpenOption)
        }
        break
      case 'CANADD':
      case 'INGREDIENT':
        if (onModifierRendered) {
          lineDesc = onModifierRendered(saleLine)
        } else {
          let lineQty = ''
          lineDesc = `${saleLine.productName}`
          if (Number(saleLine.qty) > 0) {
            lineQty = Number(saleLine.qty)
            if ((saleLine.level > 0) && (Number(parentLine.qty) > 0)) {
              lineQty *= Number(parentLine.qty)
            }
            lineQty = getQtyString(lineQty)
          }
          if (defaultQty === qty && !comments.length) {
            // no need to render default ingredients
            return null
          }
          if (comments.length) {
            const commentKeys = _.keys(modCommentPrefixes)
            _.forEach(comments, (comment) => {
              const commentAttr = (comment || {})['@attributes'] || {}
              if (_.includes(commentKeys, commentAttr.comment)) {
                lineDesc = `${modCommentPrefixes[commentAttr.comment]}${lineDesc}`
                ignoreComments.push(commentAttr.commentId)
              }
            })
          }
          if (_.has(modQtyPrefixes, qty)) {
            lineDesc = modQtyPrefixes[qty] + lineDesc
          }
          if (lineDesc === saleLine.productName) {
            lineDesc = `${lineQty}${saleLine.productName}`
          }
        }
        break
      case 'PRODUCT':
      case 'COMBO':
        if ((saleLine.level === 0) && (saleLine.lineNumber !== 1)) {
          separator = <div className={classes.salePanelItemSeparator}/>
        }
        if (onItemRendered) {
          lineDesc = onItemRendered(saleLine)
        } else {
          let lineQty = Number(saleLine.qty)
          if ((saleLine.level > 0) && (Number(parentLine.qty) > 0)) {
            lineQty *= Number(parentLine.qty)
          }
          lineDesc = `${getQtyString(lineQty)}${saleLine.productName}`
        }
        break
      default:
    }

    // check if there is any additional element to be appended
    let appendContent = null
    if (onLineRendered && this.props.isLastLine) {
      appendContent = onLineRendered(saleLine.lineNumber)
    }

    const key = [saleLine.lineNumber, saleLine.level, saleLine.itemId, saleLine.partCode].join('.')
    const symbol = isRefund ? currencySymbolNegative : currencySymbol
    const lineClasses = [classes.salePanelItemRoot]
    const levelClass = `salePanelItemLevel${level}`
    if (_.has(classes, levelClass)) {
      lineClasses.push(classes[levelClass])
    } else {
      lineClasses.push(`sale-panel-item-level${level}`)
    }
    if (_.isEqual(saleLine, this.props.selectedLine) ||
      _.isEqual(saleLine, this.props.selectedParent)) {
      lineClasses.push('selected')
    }
    const priceClasses = [classes.salePanelItemPrice]
    if (isRefund) {
      priceClasses.push(classes.salePanelItemNegativePrice)
    }
    const itemDiscount = Number(saleLine.itemDiscount || 0)
    if (itemDiscount > 0) {
      priceClasses.push(classes.salePanelItemPriceDiscount)
    }
    if (isModifier) {
      lineClasses.push(classes.salePanelItemModifier)
    }
    const hasPrice = saleLine.itemPrice && Number(saleLine.itemPrice) !== Number(0)
    let price = ''
    if (hasPrice) {
      let itemPrice
      if ((saleLine.level > 0) && (Number(parentLine.qty) > 0)) {
        itemPrice = Number(saleLine.itemPrice) * parentLine.qty
      } else {
        itemPrice = Number(saleLine.itemPrice)
      }
      price = ensureDecimals(
        (!showDiscountedPrice) ? itemPrice : (itemPrice - itemDiscount),
        currencyDecimals,
        decimalSeparator
      )
    }

    const lineContent = (
      <>
        {linePrefix}
        {showHoldAndFire &&
      <div className={classes.salePanelItemIconContainer}>
        {hold && <div className={classes.salePanelItemIcon}><i className="far fa-hand-paper"/></div>}
        {fire && <div className={classes.salePanelItemIcon}><i className="fas fa-bolt"/></div>}
        {highPriority && <div className={classes.salePanelItemIcon}><i className="fas fa-star"/></div>}
        {course && <div className={classes.salePanelItemIcon}><i className="fas fa-code-branch"/></div>}
        {dontMake && <div className={classes.salePanelItemIcon}><i className="fas fa-ban"/></div>}
      </div>
        }
        <div className={descClasses.join(' ')}>{lineDesc}</div>
        <div className={priceClasses.join(' ')}>
          {hasPrice && <div>{symbol}{price}</div>}
        </div>
        {showSeatInSalePanelLine &&
          <div className={classes.salePanelItemSeat}>
            {(seat != null && seat !== '0') && <div>[{seat}]</div>}
          </div>
        }
        {this.drawArrow(saleLine)}
      </>)
    const lineProps = {
      className: lineClasses.join(' '),
      onClick: () => {
        this.props.onLineClicked(saleLine, parentLine, true, { isModifier, hiddenAncestors })
      }
    }

    const totemStyle = {
      paddingTop: '1vmin',
      paddingBottom: '1vmin'
    }

    return (
      <div key={key}>
        {separator}
        <RendererChooser
          desktop={<div {...lineProps}>{lineContent}</div>}
          mobile={<div {...lineProps}>{lineContent}</div>}
          totem={<div {...lineProps} style={{ totemStyle }}>{lineContent}</div>}
        />
        {this.addComment(level + 1, ignoreComments)}
        {appendContent}
      </div>
    )
  }
}

SalePanelItem.propTypes = {
  classes: PropTypes.object,
  currencySymbol: PropTypes.string,
  currencySymbolNegative: PropTypes.string,
  showArrowOnSelection: PropTypes.bool,
  isLastLine: PropTypes.bool,
  isRefund: PropTypes.bool,
  isModifier: PropTypes.bool,
  hiddenAncestors: PropTypes.number,
  onLineClicked: PropTypes.func,
  selectedLine: PropTypes.object,
  selectedParent: PropTypes.object,
  saleLine: PropTypes.object,
  parentLine: PropTypes.object,
  renderLinePrefix: PropTypes.func,
  onLineRendered: PropTypes.func,
  onOptionRendered: PropTypes.func,
  onModifierRendered: PropTypes.func,
  onItemRendered: PropTypes.func,
  onCommentRendered: PropTypes.func,
  modQtyPrefixes: PropTypes.object,
  modCommentPrefixes: PropTypes.object,
  hideQtyOneTopLevel: PropTypes.bool,
  hideQtyOneLowLevel: PropTypes.bool,
  l10n: PropTypes.object,
  showHoldAndFire: PropTypes.bool,
  showDiscountedPrice: PropTypes.bool,
  biggerFont: PropTypes.bool,
  showSeatInSalePanelLine: PropTypes.bool
}

SalePanelItem.defaultProps = {
  biggerFont: false,
  showSeatInSalePanelLine: true
}
