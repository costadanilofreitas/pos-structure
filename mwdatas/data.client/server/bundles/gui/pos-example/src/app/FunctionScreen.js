import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Button } from 'posui/button'
import { ButtonGrid } from 'posui/widgets'

const styles = {
  container: {
    width: '100%',
    height: '100%'
  },
  gridPadding: {
    padding: '0.4vh'
  },
  lightBlueBtn: {
    backgroundColor: '#a9dbfe'
  },
  greenBtn: {
    backgroundColor: '#9ddc71'
  },
  redBtn: {
    backgroundColor: '#a52a2a'
  },
  employeeButtonsGroup: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '40%',
    height: '97%'
  },
  managerButtonsGroup: {
    position: 'absolute',
    top: 0,
    left: '40%',
    width: '40%',
    height: '97%'
  },
  utilityButtonsGroup: {
    position: 'absolute',
    top: 0,
    left: '80%',
    width: '20%',
    height: '97%'
  }
}

export class FunctionScreen extends Component {

  employeeButtons = {
    0: <Button rounded={true} style={styles.redBtn} executeAction={['doVoidSale', 'True']}>Cancel Transaction</Button>,
    1: <Button rounded={true} style={styles.redBtn} executeAction={['doVoidPaidSale']}>Over Ring (Post Void)</Button>,
    10: <Button rounded={true} style={styles.lightBlueBtn} executeAction={['doReprintReceipt', 'false', 'false', 'reprint_coupon_receipt_new']}>Reprint Any Receipt</Button>,
    11: <Button rounded={true} style={styles.lightBlueBtn} executeAction={['doPrintLastReceipt', 'false', 'coupon_receipt_new']}>Reprint Last Receipt</Button>
  }

  managerButtons = {
    0: <Button rounded={true} style={styles.lightBlueBtn} executeAction={['doTransfer', '4', 'True']}>Paid Out</Button>,
    1: <Button rounded={true} style={styles.lightBlueBtn} executeAction={['doTransfer', '3', 'True']}>Paid In</Button>,
    2: <Button rounded={true} style={styles.lightBlueBtn} executeAction={['doTransfer', '2', 'True']}>Skim</Button>,
    4: <Button rounded={true} style={styles.lightBlueBtn} executeAction={['doWasteRefundTransaction', 'refund', '', 'True']}>Refund Check</Button>,
    6: <Button rounded={true} style={styles.lightBlueBtn} executeAction={['doOpenDrawer', 'True']}>Open Drawer</Button>,
    10: <Button rounded={true} style={styles.greenBtn} executeAction={['doDrawerAudit', 'true']}>Drawer Audit</Button>,
    11: <Button rounded={true} style={styles.greenBtn} executeAction={['cashReport', 'logoffuser', 'false', 'True', 'cashNew']}>Reprint Close Drawer</Button>
  }

  utilityButtons = {
    0: <Button rounded={true} style={styles.lightBlueBtn} executeAction={['openday', 'true', 'true']}>Open Day<br/>(Store Wide)</Button>,
    1: <Button rounded={true} style={styles.lightBlueBtn} executeAction={['closeday', 'true', 'true']}>Close Day<br/>(Store Wide)</Button>,
    3: <Button rounded={true} style={styles.lightBlueBtn} executeAction={['openday', 'false', 'true']}>Open Day<br/>(This POS)</Button>,
    4: <Button rounded={true} style={styles.lightBlueBtn} executeAction={['closeday', 'false', 'true']}>Close Day<br/>(This POS)</Button>,
    9: <Button rounded={true} style={styles.redBtn} onClick={this.props.onExit}>Return</Button>
  }

  render() {
    return (
      <div style={styles.container}>
        <div style={styles.employeeButtonsGroup}>
          <ButtonGrid
            styleCell={styles.gridPadding}
            direction="column"
            cols={2}
            rows={10}
            buttons={this.employeeButtons}
            title="Employee Functions"
          />
        </div>
        <div style={styles.managerButtonsGroup}>
          <ButtonGrid
            styleCell={styles.gridPadding}
            direction="column"
            cols={2}
            rows={10}
            buttons={this.managerButtons}
            title="Manager Functions"
          />
        </div>
        <div style={styles.utilityButtonsGroup}>
          <ButtonGrid
            styleCell={styles.gridPadding}
            direction="column"
            cols={1}
            rows={10}
            buttons={this.utilityButtons}
            title="Utility"
          />
        </div>
      </div>
    )
  }
}

FunctionScreen.propTypes = {
  onExit: PropTypes.func.isRequired
}

export default FunctionScreen
