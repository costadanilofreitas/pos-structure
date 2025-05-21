import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { omit } from 'lodash'
import { I18N } from '3s-posui/core'
import { SalePanel } from './sale-panel'

import OrderPropTypes from '../../../prop-types/OrderPropTypes'
import { ensureArray, shallowIgnoreEquals } from '../../../util/renderUtil'
import MessageBusPropTypes from '../../../prop-types/MessageBusPropTypes'


class SalePanelComponent extends Component {
  constructor(props) {
    super(props)

    this.handleHeaderRendered = this.handleHeaderRendered.bind(this)
    this.changeQuantity = this.changeQuantity.bind(this)
    this.deleteLines = this.deleteLines.bind(this)
  }

  shouldComponentUpdate(nextProps) {
    return !shallowIgnoreEquals(this.props, nextProps, 'getMessage', 'classes', 'builds')
  }

  render() {
    const {
      classes,
      order,
      customOrder,
      builds,
      showSaleItemOptions,
      onUnselectLine,
      saleSummaryStyle,
      styleOverflow,
      salePanelBackground,
      products
    } = this.props

    const newProps = omit(this.props, 'classes', 'order')

    const comment1 = this.props.getMessage('$ONSIDE').toUpperCase()
    const comment2 = this.props.getMessage('$LIGHT').toUpperCase()
    const comment3 = this.props.getMessage('$EXTRA').toUpperCase()

    if (customOrder != null && customOrder.SaleLine != null) {
      customOrder.SaleLine = ensureArray(customOrder.SaleLine)
      customOrder.SaleLine.forEach((saleLine, idx) => {
        if (customOrder.SaleLine[idx] == null) {
          return
        }
        if (typeof customOrder.SaleLine[idx]['@attributes'].customProperties !== 'string') {
          return
        }
        customOrder.SaleLine[idx]['@attributes'].customProperties = JSON.parse(saleLine['@attributes'].customProperties)
      })
    }

    return (
      <SalePanel
        builds={builds}
        showSummary={true}
        showCoupons={false}
        showSummaryDue={true}
        showSummaryTax={false}
        showDiscountedPrice={true}
        showNotRequiredOptions={false}
        onHeaderRendered={this.handleHeaderRendered}
        onUnselectLine={onUnselectLine}
        modQtyPrefixes={{ 0: 'SEM ' }}
        modCommentPrefixes={{ '[OnSide]': `${comment1} `, '[Light]': `${comment2} `, '[Extra]': `${comment3} ` }}
        {...newProps}
        className={classes.salePanel}
        order={customOrder || order}
        changeQuantity={this.changeQuantity}
        deleteLines={this.deleteLines}
        showSaleItemOptions={showSaleItemOptions}
        saleSummaryStyle={saleSummaryStyle}
        styleOverflow={styleOverflow}
        salePanelBackground={salePanelBackground}
        products={products}
      />
    )
  }

  handleHeaderRendered() {
    const { classes, order, customOrder } = this.props
    let customerName = ((customOrder || order).CustomOrderProperties || {}).CUSTOMER_NAME
    let customerDoc = ((customOrder || order).CustomOrderProperties || {}).CUSTOMER_DOC

    customerName = customerName === 'None' ? null : customerName
    customerDoc = customerDoc === 'None' ? null : customerDoc
    if (!customerName && !customerDoc) {
      return null
    }

    return (
      <>
        { customerName != null &&
        <div className={classes.customerNameLine}>
          <I18N id="$SALE_CUSTOMER_NAME"/>
          <em>{customerName}</em>
        </div>
        }
        { customerDoc != null &&
        <div className={classes.customerNameLine}>
          <I18N id="$SALE_CUSTOMER_DOC"/>:
          <em> {customerDoc}</em>
        </div>
        }
      </>
    )
  }

  changeQuantity(lineNumber, currentQuantity, increase) {
    if (increase) {
      this.props.msgBus.action('doChangeQuantity', lineNumber, 1, false)
    } else if (currentQuantity > 1) {
      this.props.msgBus.action('doChangeQuantity', lineNumber, -1, false)
    }
  }

  deleteLines(linesNumber) {
    this.props.msgBus.syncAction('do_void_lines', linesNumber.join('|'))
  }
}


SalePanelComponent.propTypes = {
  builds: PropTypes.object,
  classes: PropTypes.object,
  order: OrderPropTypes,
  customOrder: OrderPropTypes,
  msgBus: MessageBusPropTypes,
  getMessage: PropTypes.func,
  showSaleItemOptions: PropTypes.bool,
  onUnselectLine: PropTypes.func,
  saleSummaryStyle: PropTypes.string,
  styleOverflow: PropTypes.bool,
  salePanelBackground: PropTypes.bool,
  products: PropTypes.object
}

SalePanelComponent.defaultProps = {
  salePanelBackground: true
}

SalePanel.defaultProps = {
  showSaleItemOptions: false,
  saleSummaryStyle: 'saleSummaryLineRoot',
  styleOverflow: false
}


export default SalePanelComponent

