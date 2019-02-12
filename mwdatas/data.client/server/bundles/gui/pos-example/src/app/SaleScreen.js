import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Button } from 'posui/button'
import { ButtonGrid, SaleTypeSelector } from 'posui/widgets'
import { SalePanel } from 'posui/sale-panel'

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
  tabs: {
    position: 'relative',
    backgroundColor: 'white',
    width: '100%',
    height: '8%',
    top: 0,
    left: 0
  },
  tabsCont: {
    position: 'absolute',
    backgroundColor: '#455A64',
    width: '100%',
    height: '92%',
    top: '8%',
    left: 0
  },
  saleButtonsCont: {
    position: 'absolute',
    top: 0,
    height: '100%',
    left: '6%',
    width: '94%'
  },
  tabButton: {
  },
  tabButtonSelected: {
    backgroundColor: 'white'
  },
  qtyButton: {
  },
  qtyButtonSelected: {
    backgroundColor: '#dddddd'
  },
  qtyCont: {
    position: 'relative',
    width: '6%',
    height: '100%',
    top: 0,
    left: 0
  }
}

class SaleScreen extends Component {

  state = {
    showFunctionScreen: false,
    selectedTabIdx: 0,
    selectedQty: 1
  }

  handleTabClicked = (idx) => {
    this.setState({ selectedTabIdx: idx })
  }

  renderTabs() {
    const { navigation } = this.props
    const { selectedTabIdx } = this.state
    const tabs = (navigation[1] || {}).groups || []
    const numTabs = tabs.length
    const tabButtons = _.zipObject(
      _.range(numTabs),
      _.map(tabs, (tab, idx) => {
        const selected = (idx === selectedTabIdx)
        return (
          <Button
            key={`${idx}_${selected}`}
            style={{ ...styles.tabButton, ...((selected) ? styles.tabButtonSelected : {}) }}
            onClick={() => this.handleTabClicked(idx)}
          >{tab.text}</Button>
        )
      })
    )
    return (
      <ButtonGrid
        direction="row"
        cols={numTabs}
        rows={1}
        buttons={tabButtons}
      />
    )
  }

  handleQtyButtonClicked = (qty) => {
    this.setState({ selectedQty: qty })
  }

  handleAnyQtyButton = (response) => {
    const qty = parseInt(response, 10)
    if (qty > 0) {
      this.setState({ selectedQty: qty })
    }
  }

  renderQtyButtons() {
    const { selectedQty } = this.state
    const buttons = _.map(_.range(1, 11), (qty) => {
      const selected = (qty === selectedQty)
      return (
        <Button
          key={`${qty}_${selected}`}
          style={{ ...styles.qtyButton, ...((selected) ? styles.qtyButtonSelected : {}) }}
          onClick={() => this.handleQtyButtonClicked(qty)}
        >{qty}</Button>
      )
    })
    buttons.push((
      <Button
        key="select_qty"
        style={styles.qtyButton}
        executeAction={['requestQuantity']}
        onActionFinish={(response) => this.handleAnyQtyButton(response)}
      >...</Button>
    ))
    const qtyButtons = _.zipObject(_.range(11), buttons)
    return (
      <ButtonGrid
        direction="column"
        cols={1}
        rows={11}
        buttons={qtyButtons}
      />
    )
  }

  sellItem = (plu) => {
    const qty = this.state.selectedQty
    this.handleQtyButtonClicked(1)
    return ['doSale', plu, qty]
  }

  render() {
    const { order, onShowFunctionScreen } = this.props
    const attributes = order['@attributes'] || {}
    const inProgress = _.includes(['IN_PROGRESS', 'TOTALED'], attributes.state)
    const { selectedLine } = this.state
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
              selectedLine={selectedLine}
              showSummary={true}
              showSummaryOnFinished={true}
              onLineClicked={(line) => { this.setState({ selectedLine: line }) }}
            />
          </div>
          <div style={styles.functionBox}>
            {inProgress &&
              <Button executeAction={['doTotal']}>Pay</Button>
            }
            {!inProgress &&
              [
                <Button key="sign_out" style={{ width: '50%', float: 'left' }} executeAction={['signOut']}>Sign out</Button>,
                <Button key="functions" style={{ width: '50%', float: 'right' }} onClick={onShowFunctionScreen}>Functions</Button>
              ]
            }
          </div>
        </div>
        <div style={styles.rightPanel}>
          <div style={styles.tabs}>
            {this.renderTabs()}
          </div>
          <div style={styles.tabsCont}>
            <div style={styles.qtyCont}>
              {this.renderQtyButtons()}
            </div>
            <div style={styles.saleButtonsCont}>
              <ButtonGrid
                direction="column"
                cols={7}
                rows={7}
                buttons={{
                  0: <Button executeAction={() => this.sellItem('1.2001')}>Sell Something</Button>
                }}
                title="Test Products"
              />
            </div>
          </div>
        </div>
      </div>
    )
  }
}

SaleScreen.propTypes = {
  /**
   * Order state from `orderReducer`
   */
  order: PropTypes.object,
  /**
   * Navigation state from `navigationReducer`
   */
  navigation: PropTypes.object,
  /**
   * Called when the users wants to show the function screen
   */
  onShowFunctionScreen: PropTypes.func.isRequired
}

SaleScreen.defaultProps = {
  order: {},
  navigation: {}
}

function mapStateToProps(state) {
  return {
    order: state.order,
    navigation: state.navigation
  }
}

export default connect(mapStateToProps)(SaleScreen)
