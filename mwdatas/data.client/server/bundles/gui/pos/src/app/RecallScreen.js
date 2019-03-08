import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { MessageBus, I18N } from 'posui/core'
import { Button } from 'posui/button'
import { ScrollPanel, DataTable } from 'posui/widgets'
import { xmlToJson, parseXml, ensureArray } from 'posui/utils'
import injectSheet, { jss } from 'react-jss'
import _ from 'lodash'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = (theme) => ({
  container: {
    position: 'absolute',
    display: 'flex',
    flexDirection: 'column',
    width: '100%',
    height: '100%'
  },
  absoluteWrapper: {
    position: 'absolute',
    width: '100%',
    height: '100%'
  },
  titlePanel: {
    flexGrow: 1,
    flexShrink: 0,
    flexBasis: 0,
    padding: '2vh 2%',
    position: 'relative'
  },
  title: {
    fontSize: '2.5vh',
    color: theme.color,
    textTransform: 'uppercase',
    paddingLeft: '2%',
    position: 'relative',
    float: 'left'
  },
  refresh: {
    backgroundColor: 'transparent',
    color: theme.color + '!important',
    position: 'relative',
    float: 'right',
    width: '30px !important',
    right: '2%'
  },
  ordersPanel: {
    position: 'relative',
    flexGrow: 99,
    flexShrink: 0,
    flexBasis: 0,
    margin: '0 2% 2vh'
  },
  ordersCont: {
    position: 'relative',
    color: '#000000',
    textAlign: 'center',
    whiteSpace: 'pre',
    width: '100%',
    height: '100%',
    border: '1px solid #e8e5e0',
    boxSizing: 'border-box'
  },
  orders: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    padding: '2vh 2%',
    boxSizing: 'border-box'
  },
  loadingSpinner: {
    composes: 'fa fa-spinner fa-spin fa-4x loading-screen-spinner',
    color: '#777777',
    width: '64px',
    height: '64px',
    position: 'fixed',
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
    margin: 'auto',
    maxWidth: '100%',
    maxHeight: '100%',
    overflow: 'hidden'
  }
})

const ActionButton = (props) => (
  <Button
    rounded={true}
    style={{
      backgroundColor: '#b9663d',
      color: 'white',
      margin: '0.2vh',
      height: '4vh',
      width: '31%',
      float: 'right'
    }}
    {...props}
  />
)

class RecallScreen extends PureComponent {

  constructor(props) {
    super(props)
    this.msgBus = new MessageBus(this.props.posId)
    this.columns = [
      {
        path: 'orderId',
        title: <I18N id="$ORDER_ID" defaultMessage="Order Id" />
      },
      {
        path: 'session.pos',
        title: <I18N id="$POS" defaultMessage="POS" />
      },
      {
        path: 'createdAtTime',
        title: <I18N id="$TIME" defaultMessage="Time" />
      },
      {
        path: 'custom.CUSTOMER_NAME',
        title: <I18N id="$CUSTOMER" defaultMessage="Customer" />
      },
      {
        path: 'custom.TAB',
        title: <I18N id="$TAB" defaultMessage="Tab" />
      },
      {
        path: 'session.user',
        title: <I18N id="$OPERATOR" defaultMessage="Operator" />
      },
      {
        path: null,
        title: <I18N id="$ACTION" defaultMessage="Action" />,
        onRenderCell: this.actionRenderer
      }
    ]
  }

  state = {
    loading: true,
    orders: []
  }

  actionRenderer = (line) => {
    return (
      <div>
        <ActionButton executeAction={['doRecallNext', '', line.orderId]}>
          <I18N id="$RECALL" defaultMessage="Recall" />
        </ActionButton>
        <ActionButton executeAction={['doPreviewOrder', line.orderId, line.session.pos]}>
          <I18N id="$ORDER_PREVIEW" defaultMessage="Preview" />
        </ActionButton>
        <ActionButton executeAction={['doVoidStoredOrder', line.orderId, line.session.pos]}>
          <I18N id="$CANCEL" defaultMessage="Cancel" />
        </ActionButton>
      </div>
    )
  }

  /**
   * Helper function to parse input XML and convert it to json
   */
  formatOrders = (xmlStr) => {
    const orders = []
    try {
      const json = xmlToJson(parseXml(xmlStr))
      _.forEach(ensureArray((json.Orders || {}).Order || []), (line) => {
        // convert custom order properties to object
        const custom = {}
        _.forEach(ensureArray((line.CustomOrderProperties || {}).OrderProperty || []), (prop) => {
          const propAttr = prop['@attributes'] || {}
          if (propAttr.key) {
            custom[propAttr.key] = propAttr.value
          }
        })
        const attrs = line['@attributes'] || {}
        // parse session
        const session = {}
        _.forEach((attrs.sessionId || '').split(',') || [], (sessionProp) => {
          const splittedSessionProp = sessionProp.split('=') || []
          if (splittedSessionProp.length > 1) {
            session[splittedSessionProp[0]] = splittedSessionProp[1]
          }
        })
        const createdAtTime = attrs.createdAt.split('T')[1]
        orders.push({
          ...attrs,
          createdAtTime,
          session,
          custom
        })
      })
    } catch (e) {
      console.warn(e)
    }
    return orders
  }

  retrieveOrders = () => {
    const { posId } = this.props
    const data = ['STORED', '', '', '', '', '', '', '', '', '', '', '', '1', ''].join('\0')

    this.setState({ loading: true })
    this.msgBus.sendMessage(
      `ORDERMGR${posId}`,
      'ORDERMGR',
      'TK_SLCTRL_OMGR_LISTORDERS',
      'param',
      10000000,
      data
    )
    .then((result) => {
      if (!result.ok) {
        return
      }
      try {
        const xmlStr = result.data.split('\0')[2]
        this.setState({
          loading: false,
          orders: this.formatOrders(xmlStr)
        })
      } catch (e) {
        console.warn(e)
      }
    })
  }

  componentDidMount() {
    this.retrieveOrders()
  }

  render() {
    const { classes } = this.props
    const { loading, orders } = this.state
    const hasOrders = (orders || []).length > 0

    return (
      <div className={classes.container}>
        <div className={classes.titlePanel}>
          <div className={classes.title}>
            <I18N id="$SAVED_ORDERS" defaultMessage="Saved Orders" />
          </div>
          <Button className={classes.refresh} onClick={this.retrieveOrders}>
            <i className="fa fa-refresh fa-2x" aria-hidden="true"/>
          </Button>
        </div>
        <div className={classes.ordersPanel}>
          <div className={classes.absoluteWrapper}>
            <div className={classes.ordersCont}>
              <div className={classes.orders}>
                {loading && <div className={classes.loadingSpinner} />}
                {(!loading && hasOrders) &&
                  <ScrollPanel styleCont={{ fontWeight: 'normal' }}>
                    <DataTable
                      style={{ borderCollapse: 'collapse' }}
                      styleHeaderRow={{ height: '7vh' }}
                      styleRow={{ height: '7vh', borderTop: '1px solid #cccccc' }}
                      columns={this.columns}
                      data={orders}
                    />
                  </ScrollPanel>
                }
                {(!loading && !hasOrders) &&
                  <div><I18N id="$NO_ORDERS_FOUND" defaultMessage="No orders found!" /></div>
                }
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }
}

RecallScreen.propTypes = {
  /**
   * Injected classes
   * @ignore
   */
  classes: PropTypes.object,
  /**
   * POS id from `posIdReducer` app state
   * @ignore
   */
  posId: PropTypes.number
}


function mapStateToProps({ posId }) {
  return {
    posId
  }
}

export default connect(mapStateToProps)(injectSheet(styles)(RecallScreen))

