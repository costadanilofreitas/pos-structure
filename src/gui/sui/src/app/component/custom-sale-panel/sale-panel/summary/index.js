import React, { PureComponent } from 'react'
import _ from 'lodash'
import injectSheet, { jss } from 'react-jss'

import { ensureArray, ensureDecimals } from '3s-posui/utils'
import { ScrollPanel } from '3s-widgets'

import SaleSummaryLine from '../SaleSummaryLine'

import styles from './styles'
import propTypes, { defaultProps } from './propTypes'


jss.setup({ insertionPoint: 'posui-css-insertion-point' })

class Index extends PureComponent {
  constructor(props) {
    super(props)

    this.scrollPanel = null
    this.scrollElement = null
    this.state = {
      fullScroll: false
    }

    this.checkScrollPanelRefresh = this.checkScrollPanelRefresh.bind(this)
  }

  render() {
    const {
      classes, deliveryPLUs, order, showSummaryOnFinished, showSummaryDue, showSummaryChange, l10n, showScrollTenders,
      saleSummaryStyle
    } = this.props

    if (!order || _.isEmpty(order)) {
      return <div/>
    }
    const currencyDecimals = l10n.CURRENCY_DECIMALS || 2
    const decimalSeparator = l10n.DECIMALS_SEPARATOR || '.'
    const orderAttr = order['@attributes'] || {}
    const discount = Number(orderAttr.discountAmount || 0)
    let totAmountAD = Number(orderAttr.totalAfterDiscount || 0)
    const totTax = Number(orderAttr.taxTotal || 0)
    let totAmount = Number(orderAttr.totalGross || 0)
    const totTender = Number(orderAttr.totalTender || 0)
    const dueAmount = Number(orderAttr.dueAmount || 0)
    const change = Number(orderAttr.change || 0)
    const orderTip = Number(orderAttr.tip || 0)
    const priceBasis = orderAttr.priceBasis || 'G'
    let tip = Number(0)
    let deliveryCharge = 0
    const serviceCharge = Number(orderAttr.serviceCharge || 0)
    let subtotAmount = Number(orderAttr.totalAmount || 0)

    if (showSummaryOnFinished && _.includes(['IN_PROGRESS', 'TOTALED'], orderAttr.state)) {
      return <div/>
    }

    _.forEach(ensureArray(order.SaleLine || []), (saleLine) => {
      const saleLineAttr = saleLine['@attributes']
      if (_.includes(deliveryPLUs, saleLineAttr.partCode) && Number(saleLineAttr.qty) !== 0) {
        deliveryCharge = Number(saleLineAttr.itemPrice || '0.00')
        // subtotal should not include delivery charge, so we need to subtract it
        subtotAmount -= deliveryCharge
        if (!isNaN(serviceCharge)) {
          subtotAmount -= serviceCharge
        }
      }
    })

    if (orderTip === 0) {
      _.forEach(ensureArray((order.TenderHistory || {}).Tender || []), (tenderTip) => {
        const tenderAttr = tenderTip['@attributes'] || {}
        tip += Number(tenderAttr.tip || '0.00')
      })
    } else {
      tip = orderTip
    }

    if (tip > 0) {
      totAmount += tip
    }

    let tenders = []
    let summaryPayment = null
    if (_.includes(['PAID', 'STORED', 'TOTALED'], (order['@attributes'] || {}).state)) {
      tenders = ensureArray((order.TenderHistory || {}).Tender || [])
        .map((item) => {
          const tenderAttr = item['@attributes']
          const tenderAmount = Number(tenderAttr.tenderAmount)
          return (
            <SaleSummaryLine
              saleSummaryStyle={saleSummaryStyle}
              translate={false}
              label={`${tenderAttr.tenderDescr} :`}
              defaultMessage={tenderAttr.tenderDescr}
              key={tenderAttr.timestamp}
              value={ensureDecimals(tenderAmount, currencyDecimals, decimalSeparator)}
            />
          )
        })
      summaryPayment =
        <div>
          <div className={classes.saleSummarySeparator}/>
          {tenders}
          <SaleSummaryLine
            saleSummaryStyle={saleSummaryStyle}
            label="$LABEL_PAID_AMOUNT"
            defaultMessage="Paid    : {0}"
            value={ensureDecimals(totTender, currencyDecimals, decimalSeparator)}
          />
          {showSummaryChange &&
          <SaleSummaryLine
            saleSummaryStyle={saleSummaryStyle}
            label="$LABEL_CHANGE_AMOUNT"
            defaultMessage="Change  : {0}"
            value={ensureDecimals(change, currencyDecimals, decimalSeparator)}
            className={(change > 0) ? classes.saleSummaryChangeLine : ''}
          />}
          {(showSummaryDue && dueAmount !== 0) &&
          <SaleSummaryLine
            saleSummaryStyle={saleSummaryStyle}
            label="$LABEL_DUE_AMOUNT"
            defaultMessage="Due     : {0}"
            value={ensureDecimals(dueAmount, currencyDecimals, decimalSeparator)}
            className={classes.saleSummaryDueLine}
          />}
          <div ref={(el) => {
            this.scrollElement = el
          }} style={{ minHeight: '1px' }}
          />
        </div>
    }

    if (priceBasis === 'G') {
      subtotAmount += totTax
      totAmountAD += totTax
    }

    const details = this.renderDetails(
      subtotAmount,
      currencyDecimals,
      decimalSeparator,
      deliveryCharge,
      serviceCharge,
      discount,
      totAmountAD,
      totTax,
      tip,
      totAmount,
      summaryPayment,
      order
    )

    if (showScrollTenders !== true) {
      this.scrollPanel = null
    }
    return (
      <div className={classes.salePanelSummary}>
        {showScrollTenders
          ?
          <ScrollPanel reference={(el) => {
            this.scrollPanel = el
          }}
          >
            {details}
          </ScrollPanel>
          :
          details
        }
      </div>
    )
  }

  checkScrollPanelRefresh() {
    if (this.scrollPanel != null && this.scrollElement != null) {
      this.scrollPanel.ensureVisible(this.scrollElement)
      if (this.state.fullScroll === false) {
        this.setState({ fullScroll: true })
      }
    } else if (this.props.showScrollTenders === false && this.state.fullScroll === true) {
      this.setState({ fullScroll: false })
    }
  }

  componentDidUpdate() {
    this.checkScrollPanelRefresh()
  }

  componentDidMount() {
    this.checkScrollPanelRefresh()
  }

  renderDetails(
    subtotAmount,
    currencyDecimals,
    decimalSeparator,
    deliveryCharge,
    serviceCharge,
    discount,
    totAmountAD,
    totTax,
    tip,
    totAmount,
    summaryPayment
  ) {
    const {
      classes, showSummarySubtotal, showSummaryDelivery, showSummaryService, showSummaryDiscount, summaryCustomBottom,
      showSummaryTotalAfterDiscount, showSummaryTax, showSummaryTotal, showSummaryTip, summaryCustomTop,
      saleSummaryStyle, showSummaryPayment
    } = this.props

    const hasCustomTop = Boolean(summaryCustomTop)
    const hasCustomBottom = Boolean(summaryCustomBottom)

    return <>
      {hasCustomTop &&
      summaryCustomTop
      }
      {hasCustomTop &&
      <div className={classes.saleSummarySeparator}/>
      }
      {showSummarySubtotal &&
      <SaleSummaryLine
        saleSummaryStyle={saleSummaryStyle}
        label="$LABEL_SUBTOTAL_AMOUNT"
        defaultMessage="Subtotal: {0}"
        value={ensureDecimals(subtotAmount, currencyDecimals, decimalSeparator)}
      />
      }
      {(showSummaryDelivery && deliveryCharge > 0) &&
      <SaleSummaryLine
        saleSummaryStyle={saleSummaryStyle}
        label="$LABEL_DELIVERY_AMOUNT"
        defaultMessage="Delivery: {0}"
        value={ensureDecimals(deliveryCharge, currencyDecimals, decimalSeparator)}
      />
      }
      {(showSummaryService && serviceCharge > 0) &&
      <SaleSummaryLine
        saleSummaryStyle={saleSummaryStyle}
        label="$LABEL_SERVICE_CHARGE_AMOUNT"
        defaultMessage="Service : {0}"
        value={ensureDecimals(serviceCharge, currencyDecimals, decimalSeparator)}
      />
      }
      {(showSummaryDiscount && discount > 0) &&
      <SaleSummaryLine
        saleSummaryStyle={saleSummaryStyle}
        label="$LABEL_DISCOUNT_AMOUNT"
        defaultMessage="Discount: {0}"
        value={ensureDecimals(discount, currencyDecimals, decimalSeparator)}
        className="sale-summary-discount-line"
      />
      }
      {(showSummaryDiscount && discount < 0) &&
      <SaleSummaryLine
        saleSummaryStyle={saleSummaryStyle}
        label="$LABEL_ADDITION_AMOUNT"
        value={ensureDecimals(Math.abs(discount), currencyDecimals, decimalSeparator)}
        className="sale-summary-discount-line"
      />
      }
      {(showSummaryTotalAfterDiscount && discount > 0) &&
      <SaleSummaryLine
        saleSummaryStyle={saleSummaryStyle}
        label="$LABEL_TOTAL_AFTER_DISCOUNT"
        defaultMessage="Total w/ Discount: {0}"
        value={ensureDecimals(totAmountAD, currencyDecimals, decimalSeparator)}
      />
      }
      {showSummaryTax &&
      <SaleSummaryLine
        saleSummaryStyle={saleSummaryStyle}
        label="$LABEL_TAX_AMOUNT"
        defaultMessage="Tax     : {0}"
        value={ensureDecimals(totTax, currencyDecimals, decimalSeparator)}
      />
      }
      {(showSummaryTip && tip > 0) &&
      <SaleSummaryLine
        saleSummaryStyle={saleSummaryStyle}
        label="$LABEL_TIP_AMOUNT"
        defaultMessage="Tip     : {0}"
        value={ensureDecimals(tip, currencyDecimals, decimalSeparator)}
      />
      }
      {showSummaryTotal &&
      <SaleSummaryLine
        saleSummaryStyle={saleSummaryStyle}
        label="$LABEL_TOTAL_AMOUNT"
        defaultMessage="Total   : {0}"
        value={ensureDecimals(totAmount, currencyDecimals, decimalSeparator)}
        className={classes.saleSummaryTotalLine}
      />
      }
      {showSummaryPayment &&
      summaryPayment
      }
      {hasCustomBottom &&
      <div className={classes.saleSummarySeparator}/>
      }
      {hasCustomBottom &&
      summaryCustomBottom
      }
    </>
  }
}

Index.propTypes = propTypes
Index.defaultProps = defaultProps

export default injectSheet(styles)(Index)
