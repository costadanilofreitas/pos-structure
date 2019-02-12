import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Button } from 'posui/button'
import { ButtonGrid, SaleTypeSelector, NumPad } from 'posui/widgets'
import { SalePanel } from 'posui/sale-panel'
import { ensureDecimals } from 'posui/utils'

const styles = {
  leftPanel: {
    position: 'absolute',
    backgroundColor: '#607D8B',
    top: 0,
    left: 0,
    width: '32%',
    height: '97%'
  },
  saleTypeBox: {
    position: 'absolute',
    top: 0,
    width: '100%',
    height: '10%'
  },
  salePanelBox: {
    position: 'absolute',
    top: '10%',
    width: '100%',
    height: '75%'
  },
  functionBox: {
    position: 'absolute',
    bottom: 0,
    width: '100%',
    height: '15%'
  },
  rightPanel: {
    position: 'absolute',
    backgroundColor: '#546E7A',
    top: 0,
    left: '32%',
    width: '68%',
    height: '97%'
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
    padding: '2.5vh'
  },
  tenderQuickGrid: {
    paddingBottom: '8vh'
  }
}

class TenderScreen extends Component {
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
    const amount = Number((props.order['@attributes'] || {}).totalGross || '0')
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

  render() {
    const { order } = this.props
    const { value } = this.state
    return (
      <div>
        <div style={styles.leftPanel}>
          <div style={styles.saleTypeBox}>
            <SaleTypeSelector />
          </div>
          <div style={styles.salePanelBox}>
            <SalePanel
              style={{ backgroundColor: 'white' }}
              order={order}
              showSummary={true}
            />
          </div>
          <div style={styles.functionBox}>
            <Button executeAction={['doBackFromTotal']}>Back to Order</Button>
          </div>
        </div>
        <div style={styles.rightPanel}>
          <div style={{ height: '60%', width: '40%', float: 'left', padding: '18vh 5%' }}>
            <NumPad
              value={value}
              onTextChange={this.handleInputChange}
              forceFocus={true}
              showDoubleZero={true}
              currencyMode={true}
              textAlign="right"
              shouldClearText={this.shouldClearText}
            />
          </div>
          <div style={{ height: '100%', width: '50%', float: 'right', position: 'relative' }}>
            <ButtonGrid
              styleCell={styles.tenderGrid}
              direction="column"
              cols={1}
              rows={4}
              buttons={{
                0: (
                  <Button
                    executeAction={['doEletronicTender', this.state.value, '1', 'False', 50000]}
                    rounded={true}
                    style={{ ...styles.tenderGreen, ...styles.bigTenderButton }}>
                    <i style={styles.tenderIcon} className="fa fa-credit-card fa-4x" aria-hidden="true"></i>
                    <div style={styles.bigTenderText}>Card</div>
                  </Button>
                ),
                1: (
                  <Button
                    executeAction={() => { return this.doTender(this.state.value, '0') }}
                    rounded={true}
                    style={{ ...styles.tenderGreen, ...styles.bigTenderButton }}>
                    <i style={styles.tenderIcon} className="fa fa-money fa-4x" aria-hidden="true"></i>
                    <div style={styles.bigTenderText}>Cash</div>
                  </Button>
                ),
                2: (
                  <div style={{ position: 'relative', height: '100%', width: '100%' }}>
                    <ButtonGrid
                      styleCell={styles.tenderQuickGrid}
                      direction="row"
                      cols={4}
                      rows={1}
                      buttons={{
                        0: (
                          <Button
                            executeAction={() => { return this.doTender(this.state.nextDollar, '0') }}
                            rounded={true}
                            style={styles.tenderGreen}>
                            ${this.state.nextDollar}
                          </Button>
                        ),
                        1: (
                          <Button
                            executeAction={() => { return this.doTender('10.00', '0') }}
                            rounded={true}>
                            $10.00
                          </Button>
                        ),
                        2: (
                          <Button
                            executeAction={() => { return this.doTender('20.00', '0') }}
                            rounded={true}>
                            $20.00
                          </Button>
                        ),
                        3: (
                          <Button
                            executeAction={() => { return this.doTender('50.00', '0') }}
                            rounded={true}>
                            $50.00
                          </Button>
                        )
                      }}
                    />
                  </div>
                )
              }}
            />
          </div>
        </div>
      </div>
    )
  }
}

TenderScreen.propTypes = {
  /**
   * Order state from `orderReducer`
   */
  order: PropTypes.object
}

TenderScreen.defaultProps = {
  order: {}
}

function mapStateToProps(state) {
  return {
    order: state.order
  }
}

export default connect(mapStateToProps)(TenderScreen)
