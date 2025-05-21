import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import _ from 'lodash'
import injectSheet, { jss } from 'react-jss'

import { I18N } from '3s-posui/core'
import SalePanelItems from './SalePanelItems'
import SaleHeader from './SaleHeader'
import SaleSummary from './summary'


jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = {
  salePanelRoot: {
    composes: 'sale-panel-root',
    boxSizing: 'border-box',
    MozBoxSizing: 'border-box',
    WebkitBoxSizing: 'border-box',
    height: '100%',
    width: '100%'
  },
  salePanelCont: {
    composes: 'sale-panel-cont',
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    position: 'relative'
  },
  salePanelContHeader: {
    composes: 'sale-panel-cont-header',
    width: '100%',
    borderBottom: '1px solid rgba(204, 204, 204, 1)',
    flex: 1,
    position: 'relative'
  },
  salePanelContItems: {
    composes: 'sale-panel-cont-items',
    width: '100%',
    flex: 8,
    position: 'relative',
    minHeight: '20vh'
  },
  observationsSeparator: {
    composes: 'sale-summary-separator',
    width: '100%',
    borderTop: '1px #cccccc',
    borderTopStyle: 'solid'
  },
  salePanelContSummary: {
    composes: 'sale-panel-cont-summary',
    width: '100%',
    position: 'relative',
    flex: 1
  }
}

class SalePanel extends PureComponent {
  getDeliveryObservations() {
    const { order } = this.props
    if (order.CustomOrderProperties) {
      const orderProperty = order.CustomOrderProperties.OrderProperty
      if (orderProperty) {
        const remoteOrderJson = orderProperty.find(idx => idx['@attributes'].key === 'REMOTE_ORDER_JSON')

        if (remoteOrderJson) {
          const parsedJson = JSON.parse(remoteOrderJson['@attributes'].value)
          return parsedJson.observations
        }
      }
    }
    return false
  }
  render() {
    const { classes, showHeader: propShowHeader, showSummary, className, style, order } = this.props
    const showHeader = propShowHeader && (order.state || '').toString().toUpperCase() !== 'PAID'
    const tenders = _.get(order, 'TenderHistory.Tender.length', 0)
    const showScrollTenders = tenders > 8
    const deliveryObservations = this.getDeliveryObservations()

    return (
      <div className={`${classes.salePanelRoot} ${className}`} style={style}>
        <div className={classes.salePanelCont}>
          {showHeader &&
          <div className={classes.salePanelContHeader}>
            <SaleHeader {..._.omit(this.props, 'classes')} />
          </div>
          }
          <div className={classes.salePanelContItems}>
            <SalePanelItems {..._.omit(this.props, 'classes')} />
          </div>
          {deliveryObservations &&
            <div>
              <div className={classes.observationsSeparator}/>
              <div style={{ padding: '0 2%' }}>
                <I18N id={'$OBSERVATION_DELIVERY_REPORT'}/>:
              &nbsp;
                {deliveryObservations}
              </div>
            </div>
          }
          {showSummary &&
          <div className={classes.salePanelContSummary} style={showScrollTenders ? { flex: 70 } : {} }>
            <SaleSummary showScrollTenders={showScrollTenders} {..._.omit(this.props, 'classes')} />
          </div>
          }
        </div>
      </div>
    )
  }
}

SalePanel.propTypes = {
  classes: PropTypes.object,
  className: PropTypes.string,
  style: PropTypes.object,
  showFinishedSale: PropTypes.bool,
  showHeader: PropTypes.bool,
  showHeaderOrderId: PropTypes.bool,
  showHeaderStatus: PropTypes.bool,
  showOrderTimer: PropTypes.bool,
  showSummary: PropTypes.bool,
  showSummaryOnFinished: PropTypes.bool,
  showSummarySubtotal: PropTypes.bool,
  showSummaryDelivery: PropTypes.bool,
  showSummaryService: PropTypes.bool,
  showSummaryDiscount: PropTypes.bool,
  showSummaryTotalAfterDiscount: PropTypes.bool,
  showSummaryTax: PropTypes.bool,
  showSummaryTotal: PropTypes.bool,
  showSummaryTip: PropTypes.bool,
  showSummaryDue: PropTypes.bool,
  showSummaryPayment: PropTypes.bool,
  showSummaryChange: PropTypes.bool,
  order: PropTypes.object,
  builds: PropTypes.object,
  autoSelectLine: PropTypes.bool,
  skipAutoSelect: PropTypes.bool,
  onLineClicked: PropTypes.func,
  trainingMode: PropTypes.bool,
  selectedLine: PropTypes.object,
  selectedParent: PropTypes.object,
  currencySymbol: PropTypes.string,
  currencySymbolNegative: PropTypes.string,
  onHeaderRendered: PropTypes.func,
  onLineRendered: PropTypes.func,
  onOptionRendered: PropTypes.func,
  onModifierRendered: PropTypes.func,
  onItemRendered: PropTypes.func,
  onCommentRendered: PropTypes.func,
  onUnselectLine: PropTypes.func,
  showArrowOnSelection: PropTypes.bool,
  deliveryPLUs: PropTypes.array,
  modQtyPrefixes: PropTypes.object,
  modCommentPrefixes: PropTypes.object,
  hideQtyOneTopLevel: PropTypes.bool,
  hideQtyOneLowLevel: PropTypes.bool,
  showPricedOptions: PropTypes.bool,
  showNotRequiredOptions: PropTypes.bool,
  showHoldAndFire: PropTypes.bool,
  l10n: PropTypes.object,
  renderLinePrefix: PropTypes.func,
  showCoupons: PropTypes.bool,
  ignorePLUs: PropTypes.array,
  summaryCustomTop: PropTypes.node,
  summaryCustomBottom: PropTypes.node,
  showDiscountedPrice: PropTypes.bool,
  changeQuantity: PropTypes.func,
  deleteLines: PropTypes.func,
  onShowModifierScreen: PropTypes.func,
  showSaleItemOptions: PropTypes.bool,
  saleSummaryStyle: PropTypes.string,
  styleOverflow: PropTypes.bool,
  biggerFont: PropTypes.bool,
  showSeatInSalePanelLine: PropTypes.bool,
  showCartMessage: PropTypes.bool,
  centralizeSummaryTotal: PropTypes.bool,
  products: PropTypes.object
}

SalePanel.defaultProps = {
  className: '',
  style: {},
  order: {},
  autoSelectLine: false,
  showFinishedSale: true,
  showHeader: true,
  showHeaderOrderId: true,
  showHeaderStatus: true,
  showOrderTimer: true,
  showSummary: false,
  showSummaryOnFinished: false,
  showSummarySubtotal: true,
  showSummaryDelivery: true,
  showSummaryService: true,
  showSummaryDiscount: true,
  showSummaryTotalAfterDiscount: true,
  showSummaryTax: true,
  showSummaryTotal: true,
  showSummaryTip: true,
  showSummaryDue: true,
  showSummaryPayment: true,
  showSummaryChange: true,
  onLineClicked: (selectedLine) => selectedLine,
  skipAutoSelect: false,
  builds: {},
  currencySymbol: '',
  currencySymbolNegative: '-',
  deliveryPLUs: [],
  modQtyPrefixes: {
    0: 'No ',
    1: '',
    2: 'Extra '
  },
  modCommentPrefixes: {
    '[On Side]': 'OS ',
    '[Light]': 'Light '
  },
  hideQtyOneTopLevel: false,
  hideQtyOneLowLevel: true,
  showPricedOptions: false,
  showNotRequiredOptions: true,
  showHoldAndFire: false,
  l10n: {},
  showCoupons: true,
  ignorePLUs: [],
  showDiscountedPrice: false,
  centralizeSummaryTotal: false
}

function mapStateToProps({ locale, trainingMode }) {
  const { l10n } = (locale || {})
  return {
    l10n,
    trainingMode
  }
}

export default connect(mapStateToProps)(injectSheet(styles)(SalePanel))
