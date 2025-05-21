import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'
import { I18N } from '3s-posui/core'
import { OrderTimer } from '3s-posui/widgets'
import injectSheet, { jss } from 'react-jss'


jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = (theme) => ({
  salePanelHeader: {
    composes: 'sale-panel-header',
    padding: '0 2%',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    height: '100%'
  },
  salePanelOrderInfoLine: {
    composes: 'sale-header-order-info-line test_SaleHeader_LIDE',
    fontSize: '1.5vh',
    display: 'flex',
    width: '100%'
  },
  salePanelOrderInfoLineText: {
    composes: 'sale-header-order-info-line-text test_SaleHeader_TEXT',
    flexGrow: 1,
    flexShrink: 0,
    flexBasis: 'auto',
    color: theme.salePanelFontColor
  },
  salePanelOrderInfoLineTimer: {
    composes: 'sale-header-order-info-line-timer test_SaleHeader_TIMER',
    flexGrow: 0,
    flexShrink: 0,
    flexBasis: 'auto',
    color: theme.salePanelFontColor
  }
})

/**
 * Helper component to display a header panel on the top of the sale panel.
 *
 * Available class names:
 * - sale header main element: `sale-panel-header`
 * - sale header line containing order id and status: `sale-header-order-info-line`
 * - text of the sale header line: `sale-header-order-info-line-text`
 * - timer of the sale header line: `sale-header-order-info-line-timer`
 */
class SaleHeader extends PureComponent {
  render() {
    const {
      classes, showHeaderOrderId, showHeaderStatus, showOrderTimer, order, onHeaderRendered
    } = this.props

    if (!order || _.isEmpty(order) || (!showHeaderOrderId && !showHeaderStatus)) {
      return <div/>
    }
    let appendContent = null
    if (onHeaderRendered != null) {
      appendContent = onHeaderRendered()
    }
    const orderAttr = order['@attributes'] || {}
    const orderId = <I18N id="$LABEL_ORDER_ID" defaultMessage="Order id: {0}" values={{ 0: orderAttr.orderId }} />
    const inProgress = _.includes(['IN_PROGRESS', 'TOTALED'], orderAttr.state)
    const stateLabelId = `$STATUS_${orderAttr.state}`
    let stateDefaultMessage
    switch (orderAttr.state) {
      case 'PAID':
        stateDefaultMessage = 'Paid'
        break
      case 'VOIDED':
        stateDefaultMessage = 'Voided'
        break
      case 'IN_PROGRESS':
        stateDefaultMessage = 'In Progress...'
        break
      case 'HELD':
        stateDefaultMessage = 'Held'
        break
      case 'STORED':
        stateDefaultMessage = 'Stored'
        break
      case 'TOTALED':
        stateDefaultMessage = 'Totaled'
        break
      case 'RECALLED':
        stateDefaultMessage = 'Recalled'
        break
      case 'SERVED':
        stateDefaultMessage = 'Served'
        break
      default:
        stateDefaultMessage = ''
    }

    const state = (orderAttr.state) ? <I18N id={stateLabelId} defaultMessage={stateDefaultMessage} /> : <div/>
    const showParentheses = Boolean(showHeaderOrderId && showHeaderStatus && orderAttr.state)
    return (
      <div className={classes.salePanelHeader}>
        <div className={classes.salePanelOrderInfoLine}>
          <div className={classes.salePanelOrderInfoLineText}>
            {showHeaderOrderId && orderId}
            {showParentheses && <span> (</span>}
            {showHeaderStatus && state}
            {showParentheses && <span>)</span>}
          </div>
          {(showOrderTimer && inProgress) &&
            <div className={classes.salePanelOrderInfoLineTimer}>
              <OrderTimer order={order} />
            </div>
          }
        </div>
        {appendContent != null && appendContent}
      </div>
    )
  }
}

SaleHeader.propTypes = {
  classes: PropTypes.object,
  order: PropTypes.object.isRequired,
  showHeaderOrderId: PropTypes.bool,
  showHeaderStatus: PropTypes.bool,
  showOrderTimer: PropTypes.bool,
  onHeaderRendered: PropTypes.func
}

SaleHeader.defaultProps = {
  order: {}
}

export default injectSheet(styles)(SaleHeader)
