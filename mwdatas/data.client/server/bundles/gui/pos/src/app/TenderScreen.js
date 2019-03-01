import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import { I18N } from 'posui/core'
import { Button } from 'posui/button'
import { ButtonGrid, SaleTypeSelector, NumPad } from 'posui/widgets'
import { SalePanel } from 'posui/sale-panel'
import { ensureDecimals } from 'posui/utils'
import injectSheet, { jss } from 'react-jss'
import TenderDivision from './TenderDivision'
import { MENU_ORDER } from '../reducers/menuReducer'
import setMenuAction from '../actions/setMenuAction'
import {DataTable, ScrollPanel} from './RecallScreen';

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = {
  flexContainerStyle: {
    display: 'flex',
    flexDirection: 'column',
    width: '100%',
    height: '100%',
    position: 'absolute'
  },
  absoluteWrapper: {
    position: 'absolute',
    width: '100%',
    height: '100%'
  },
  tenderContainer: {
    flexGrow: 90,
    flexShrink: 0,
    flexBasis: 0,
    position: 'relative'
  },
  flexTender: {
    display: 'flex',
    width: '100%',
    height: '100%',
    position: 'absolute',
    padding: '0.5vh 0.5%',
    boxSizing: 'border-box'
  },
  leftPanel: {
    flexGrow: 30,
    flexShrink: 0,
    flexBasis: 0,
    position: 'relative'
  },
  leftFlexContainer: {
    display: 'flex',
    flexDirection: 'column',
    width: '100%',
    height: '100%',
    position: 'absolute'
  },
  centerPanel: {
    flexGrow: 30,
    flexShrink: 0,
    flexBasis: 0,
    position: 'relative',
    margin: '0 1%',
    boxSizing: 'border-box'
  },
  saleTypeBox: {
    position: 'relative',
    flexGrow: 5,
    flexShrink: 0,
    flexBasis: 0,
    margin: '0.2vh 0 0.5vh',
    minHeight: '4.5vh'
  },
  salePanel: {
    backgroundColor: 'white'
  },
  salePanelBox: {
    position: 'relative',
    flexGrow: 95,
    flexShrink: 0,
    flexBasis: 0
  },
  rightPanel: {
    flexGrow: 30,
    flexShrink: 0,
    flexBasis: 0,
    position: 'relative'
  },
  footerContainer: {
    flexGrow: 10,
    flexShrink: 0,
    flexBasis: 0,
    position: 'relative'
  },
  footer: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    padding: '0.5vh 0.5%',
    boxSizing: 'border-box'
  },
  footerWrapper: {
    position: 'relative',
    width: '100%',
    height: '100%'
  },
  tenderGreen: {
    backgroundColor: '#74aa64'
  },
  bigTenderButton: {
    color: 'white',
    width: '100%',
    height: '100%',
    outline: 'none',
    border: 'none',
    fontSize: '2vh'
  },
  tenderIcon: {
    paddingBottom: '15%'
  },
  bigTenderText: {
    width: '100%',
    bottom: '20%',
    position: 'absolute',
    left: 0
  },
  tenderGrid: {
    padding: '2vh 2.5%'
  },
  gridPadding: {
    padding: '0.5vh 0.5vh'
  },
  tenderQuickGrid: {
    padding: '2.5vh 2.5%',
    width: '23%'
  },
  numPad: {
    '& table tr:first-child': {
      height: '17% !important'
    }
  },
  backToOrder: {
    backgroundColor: '#cccccc'
  },
  quickTender: {
    backgroundColor: '#0066b2'
  },
  discount: {
    backgroundColor: '#3e3c3c',
    color: '#e2dac7'
  },
  tenderDivision: {
    backgroundColor: '#3e3c3c',
    color: '#e2dac7',
    width: '100%',
    height: '100%'
  },
  functionButton: {
  },
  saveOrder: {
    backgroundColor: '#d2691e', color: 'white'
  },
  customerInfo: {
    backgroundColor: '#d2691e', color: 'white'
  },
  customerNameLine: {
    fontSize: '1.5vh',
    paddingTop: '0.4vh'
  },
}

class TenderScreen extends PureComponent {
  constructor(props) {
    super(props)

    this.initialDue = ensureDecimals(Number((this.props.order['@attributes'] || {}).dueAmount || '0'))
    this.clearCurrentText = true
    this.state = {
      value: this.initialDue,
      nextDollar: this.getNextDollar(props)
    }
  }

  getNextDollar = (props) => {
    const amount = Number((props.order['@attributes'] || {}).dueAmount || '0')
    return Math.floor((amount % 1 !== 0) ? (amount + 1) : amount) + '.00'
  }

  doTender = (amount, tenderId) => {
    return ['doTender', amount, tenderId]
  }

  handleInputChange = (value) => {
    this.setState({ value })
    return value
  }

  shouldClearText = () => {
    const clear = this.clearCurrentText
    if (clear) {
      this.clearCurrentText = false
    }
    return clear
  }

  componentWillReceiveProps(nextProps) {
    const nextDue = ensureDecimals(Number((nextProps.order['@attributes'] || {}).dueAmount || '0'))
    if (nextDue !== this.initialDue) {
      this.initialDue = nextDue
      this.clearCurrentText = true
      this.setState({ value: nextDue, nextDollar: this.getNextDollar(nextProps) })
    }
  }

  tenderButton = { ...styles.tenderGreen, ...styles.bigTenderButton }

  paymentType = {
    //  To Do Paymente card
    0: <Button executeAction={() => { return this.doTender(this.state.value, '1') }}
         rounded={true} style={this.tenderButton}>
         <i style={styles.tenderIcon} className="fa fa-credit-card fa-4x" aria-hidden="true"></i>
         <div style={styles.bigTenderText}>Credito</div>
       </Button>,
    1: <Button executeAction={() => { return this.doTender(this.state.value, '2') }}
         rounded={true} style={this.tenderButton}>
         <i style={styles.tenderIcon} className="fa fa-credit-card fa-4x" aria-hidden="true"></i>
         <div style={styles.bigTenderText}>Debito</div>
       </Button>,
    2: <Button executeAction={() => { return this.doTender(this.state.value, '3') }}
         rounded={true} style={this.tenderButton}>
         <i style={styles.tenderIcon} className="fa fa-mobile-phone fa-4x" aria-hidden="true"></i>
         <div style={styles.bigTenderText}>Maquininha</div>
       </Button>,
    3: <Button executeAction={() => { return this.doTender(this.state.value, '0') }}
         rounded={true} style={this.tenderButton}>
         <i style={styles.tenderIcon} className="fa fa-money fa-4x" aria-hidden="true"></i>
         <div style={styles.bigTenderText}>Dinheiro</div>
       </Button>
  }

  handleHeaderRendered = () => {
    const { classes, order } = this.props
    const customerName = (order.CustomOrderProperties || {}).CUSTOMER_NAME
    if (!customerName) {
      return null
    }
    return (
      <div className={classes.customerNameLine}>Customer name: <em>{customerName}</em></div>
    )
  }

  render() {
    const { order, custom, classes } = this.props
    const { value } = this.state
    const nextDolar = {
      0: <Button
           executeAction={() => { return this.doTender(this.state.nextDollar, '0') }}
           rounded={true}
           style={styles.quickTender}>
           <I18N id="$L10N_CURRENCY_SYMBOL" defaultMessage="$" /> {this.state.nextDollar}
         </Button>,
      1: <Button
           executeAction={() => { return this.doTender('10.00', '0') }}
           style={styles.quickTender}
           rounded={true}>
           <I18N id="$L10N_CURRENCY_SYMBOL" defaultMessage="$" /> 10,00
         </Button>,
      2: <Button
           executeAction={() => { return this.doTender('20.00', '0') }}
           style={styles.quickTender}
           rounded={true}>
           <I18N id="$L10N_CURRENCY_SYMBOL" defaultMessage="$" /> 20,00
         </Button>,
      3: <Button
           executeAction={() => { return this.doTender('50.00', '0') }}
           style={styles.quickTender}
           rounded={true}>
           <I18N id="$L10N_CURRENCY_SYMBOL" defaultMessage="$" /> 50,00
         </Button>
    }

    const moreFunctions = {

    }

    const discountFunctions = {

    }

    return (
      <div className={classes.flexContainerStyle}>
        <div className={classes.tenderContainer}>
          <div className={classes.flexTender} style={{ flexDirection: (custom.MIRROR_SCREEN === 'true') ? 'row-reverse' : 'row' }}>
            <div className={classes.leftPanel}>
              <div className={classes.leftFlexContainer}>
                <div className={classes.saleTypeBox}>
                  <div className={classes.absoluteWrapper}>
                    <SaleTypeSelector rounded={true} border={true} direction="row" />
                  </div>
                </div>
                <div className={classes.salePanelBox}>
                  <div className={classes.absoluteWrapper}>
                    <SalePanel
                      style={styles.salePanel}
                      order={order}
                      showSummary={true}
                      onHeaderRendered={this.handleHeaderRendered}
                    />
                  </div>
                </div>
              </div>
            </div>
            <div className={classes.centerPanel}>
              <div className={classes.absoluteWrapper}>
                <ButtonGrid
                  styleCell={styles.tenderGrid}
                  direction="row"
                  cols={2}
                  rows={2}
                  buttons={this.paymentType}
                  style={{ height: '70%', position: 'relative' }}
                />
                <ButtonGrid
                  styleCell={styles.tenderGrid}
                  direction="column"
                  cols={4}
                  rows={1}
                  buttons={nextDolar}
                  style={{ height: '15%', position: 'relative' }}
                />
                <ButtonGrid
                  styleCell={styles.tenderGrid}
                  direction="column"
                  cols={3}
                  rows={1}
                  buttons={moreFunctions}
                  style={{ height: '15%', position: 'relative' }}
                />
              </div>
            </div>
            <div className={classes.rightPanel}>
              <div className={classes.absoluteWrapper}>
                <TenderDivision
                  setNumPadValue={(value) => this.setState({value: value})}
                  style={{ height: '15%', position: 'relative' }}
                />
                <NumPad
                  className={classes.numPad}
                  value={value}
                  onTextChange={this.handleInputChange}
                  forceFocus={true}
                  showDoubleZero={true}
                  currencyMode={true}
                  textAlign="right"
                  shouldClearText={this.shouldClearText}
                  style={{ height: '70%', position: 'relative' }}
                />
                <ButtonGrid
                  styleCell={styles.tenderGrid}
                  direction="column"
                  cols={3}
                  rows={2}
                  buttons={discountFunctions}
                  style={{ height: '15%', position: 'relative' }}
                />
              </div>
            </div>
          </div>
        </div>
        <div className={classes.footerContainer}>
          <div className={classes.footer}>
            <div className={classes.footerWrapper}>
              <ButtonGrid
                styleCell={styles.gridPadding}
                direction="column"
                cols={9}
                rows={1}
                buttons={{
                  0: <Button
                       rounded={true}
                       style={styles.backToOrder}
                       executeAction={() => ['doBackFromTotal']}
                       onActionFinish={(resp) => {
                         if (resp === 'True') {
                           this.props.setMenu(MENU_ORDER)
                         }
                       }}
                       text="$BACK_TO_ORDER"
                       defaultText="Back to Order"
                     />,
                  1: <Button
                       rounded={true}
                       style={styles.customerInfo}
                       executeAction={() => ['doSetCustomerName']}
                       text="$CUSTOMER_NAME"
                       defaultText="Customer Name"
                     />,
                  2: <Button
                       rounded={true}
                       style={styles.customerInfo}
                       executeAction={() => ['doSetCustomerDocument']}
                       text="$CUSTOMER_DOC"
                       defaultText="Customer Document"
                     />,
                  8: <Button
                       rounded={true}
                       style={styles.saveOrder}
                       executeAction={['doStoreOrder']}
                       text="$SAVE_ORDER"
                       defaultText="Save Order"
                     />
                }}
              />
            </div>
          </div>
        </div>
      </div>
    )
  }
}

TenderScreen.propTypes = {
  /**
   * Injected classes
   * @ignore
   */
  classes: PropTypes.object,
  /**
   * @ignore
   */
  setMenu: PropTypes.func,
  /**
   * Order state from `orderReducer`
   */
  order: PropTypes.object,
  /**
   * Custom state from `customModelReducer`
   */
  custom: PropTypes.object
}

TenderScreen.defaultProps = {
  order: {},
  custom: {}
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators({
    setMenu: setMenuAction
  }, dispatch)
}

function mapStateToProps(state) {
  return {
    order: state.order,
    custom: state.custom
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(injectSheet(styles)(TenderScreen))
