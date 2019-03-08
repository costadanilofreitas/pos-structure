import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { MessageBus, I18N } from 'posui/core'
import { SalePanel } from 'posui/sale-panel'
import { ButtonGrid } from 'posui/widgets'
import injectSheet, { jss } from 'react-jss'

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
  ordersPanel: {
    position: 'relative',
    flexGrow: 99,
    flexShrink: 0,
    flexBasis: 0,
    margin: '0 2% 2vh'
  },
  ordersCont: {
    position: 'relative',
    backgroundColor: '#f6f5f1',
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
    textAlign: 'left',
    boxSizing: 'border-box'
  },
  orderCont: {
    position: 'absolute',
    width: '100%',
    height: '100%'
  },
  orderBack: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    backgroundColor: 'white',
    backgroundSize: 'cover',
    backgroundRepeat: 'no-repeat',
    opacity: 0.5
  },
  salePanel: {
    '& *': {
      backgroundColor: 'transparent !important',
      color: 'black !important'
    }
  }
})

class RecallByPictureScreen extends PureComponent {

  constructor(props) {
    super(props)
    this.msgBus = new MessageBus(this.props.posId)
    this.COLS = 2
    this.ROWS = 2
    this.TOTAL_CELLS = this.COLS * this.ROWS
  }

  handleRecall = (orderId) => () => {
    this.msgBus.action('doRecallByPicture', '', orderId, '')
  }

  retrieveOrders = () => {
    this.msgBus.action('showRecallByPicture', '')
  }

  componentDidMount() {
    this.retrieveOrders()
  }

  render() {
    const { classes, recallData } = this.props
    const buttons = _.reduce(
      _.slice((recallData || {}).Orders || [], 0, this.TOTAL_CELLS),
      (accum, value, index) => {
        const accumRef = accum
        const orderId = ((value || {})['@attributes'] || {}).orderId || ''
        accumRef[index] = (
          <div className={classes.orderCont} onClick={this.handleRecall(orderId)}>
            <div
              className={classes.orderBack}
              style={{ backgroundImage: `url(/mwapp/services/production/ProductionSystem?token=TK_PROD_RETRIEVEIMAGE&format=2&payload=${orderId})` }}
            />
            <SalePanel
              className={classes.salePanel}
              order={value}
              showSummary={false}
              modQtyPrefixes={{}}
            />
          </div>
        )
        return accumRef
      },
      {}
    )

    return (
      <div className={classes.container}>
        <div className={classes.titlePanel}>
          <div className={classes.title}><I18N id="$RECALL_BY_PICTURE" defaultMessage="Recall by Picture" /></div>
        </div>
        <div className={classes.ordersPanel}>
          <div className={classes.absoluteWrapper}>
            <div className={classes.ordersCont}>
              <div className={classes.orders}>
                <ButtonGrid
                  styleCell={styles.gridPadding}
                  direction="row"
                  cols={this.COLS}
                  rows={this.ROWS}
                  buttons={buttons}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }
}

RecallByPictureScreen.propTypes = {
  /**
   * Injected classes
   * @ignore
   */
  classes: PropTypes.object,
  /**
   * POS id from `posIdReducer` app state
   * @ignore
   */
  posId: PropTypes.number,
  /**
   * Recall data from `recallDataReducer` app state
   * @ignore
   */
  recallData: PropTypes.object
}


function mapStateToProps({ posId, recallData }) {
  return {
    posId,
    recallData
  }
}

export default connect(mapStateToProps)(injectSheet(styles)(RecallByPictureScreen))

