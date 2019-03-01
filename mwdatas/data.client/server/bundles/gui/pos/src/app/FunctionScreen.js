import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import _ from 'lodash'
import { I18N } from 'posui/core'
import { Button } from 'posui/button'
import { ButtonGrid } from 'posui/widgets'
import { themes } from '../constants/themes'

const styles = {
  container: {
    display: 'flex',
    width: '100%',
    height: '100%',
    position: 'absolute'
  },
  buttonsGroup: {
    flexGrow: 1,
    flexShrink: 0,
    flexBasis: 0,
    position: 'relative',
    padding: '1vh 0'
  },
  gridPadding: {
    padding: '2vh 2%'
  },
  yellowBtn: {
    backgroundColor: '#fdbd10',
    color: '#000000'
  },
  redBtn: {
    backgroundColor: '#ec1c24',
    color: '#ffffff'
  },
  disabledBtn: {
    backgroundColor: '#8e8f91',
    color: '#ffffff'
  },
  darkBtn: {
    backgroundColor: '#3f3d3d',
    color: '#ffffff'
  },
  greenBtn: {
    backgroundColor: '#CDDC39'
  }
}

export class FunctionScreen extends PureComponent {
  constructor(props) {
    super(props)
    this.availableThemes = _.join(_.map(themes, 'name'), '|')
  }

  switchServerURL = (serverurl) => {
    if (serverurl) {
      window.location = serverurl
    }
  }

  render() {
    const { custom } = this.props
    const current = (custom.MIRROR_SCREEN === 'true') ?
      <I18N id="$LEFT_HANDED" defaultMessage="Left Handed" /> :
      <I18N id="$RIGHT_HANDED" defaultMessage="Right Handed" />
    const buttons = {
      0: <Button rounded={true} className="function-btn" style={styles.yellowBtn} executeAction={['doTransfer', '2', 'True']}>
           <I18N id="$SKIM" defaultMessage="Skim" />
         </Button>,
      1: <Button rounded={true} className="function-btn" style={styles.yellowBtn} executeAction={['doTransfer', '3', 'True']}>
           <I18N id="$CASH_PAID_IN" defaultMessage="Cash Paid In" />
         </Button>,
      2: <Button rounded={true} className="function-btn" style={styles.yellowBtn} executeAction={['doReportSangria']}>
           <I18N id="$SKIM_REPORT" defaultMessage="Skim Report" />
         </Button>,
      4: <Button rounded={true} className="function-btn" style={styles.yellowBtn} executeAction={['doVoidSale', 'True','4', 'True']}>
           <I18N id="$VOID_SALE" defaultMessage="Void Sale" />
         </Button>,
      6: <Button rounded={true} className="function-btn" style={styles.greenBtn} executeAction={['importEmployees']}>
           <I18N id="$UPDATE_USERS" defaultMessage="Update Users" />
         </Button>,
      7: <Button rounded={true} className="function-btn" style={styles.redBtn} executeAction={['openday', 'false']}>
            <div>
              <I18N id="$OPEN_DAY" defaultMessage="Open Day" />
              <br/>
              (<I18N id="$THIS_POS" defaultMessage="This POS" />)
            </div>
          </Button>,
      8: <Button rounded={true} className="function-btn" style={styles.redBtn} executeAction={['closeday', 'false']}>
            <div>
              <I18N id="$CLOSE_DAY" defaultMessage="Close Day" />
              <br/>
              (<I18N id="$THIS_POS" defaultMessage="This POS" />)
            </div>
          </Button>,
      9: <Button rounded={true} className="function-btn" style={styles.redBtn} executeAction={['storewideRestart']}>
            <I18N id="$STOREWIDE_RESTART" defaultMessage="Storewide Restart" />
          </Button>,
	  10: <Button rounded={true} className="function-btn" style={styles.redBtn} executeAction={['doOpenDrawer', 'True']}>
            <I18N id="$OPEN_DRAWER" defaultMessage="Open Drawer" />
          </Button>, 
	  12:<Button rounded={true} className="function-btn" style={styles.greenBtn} executeAction={['doVoidPaidSale', 'false', 'true', 'true']}>
           <I18N id="$CLOSED_ORDERS" defaultMessage="Closed Orders" />
         </Button>,
      13:<Button rounded={true} className="function-btn" style={styles.redBtn} executeAction={['doToggleMirrorScreen']}>
           <I18N id="$MIRROR_SCREEN" defaultMessage="Mirror Screen" />
         </Button>,
      14: <Button rounded={true} className="function-btn" style={styles.darkBtn} executeAction={['cashReport', 'ask', 'RealDate']}>
            <I18N id="$RESTAURANT_SALES_REAL_DATE" defaultMessage="Restaurant Sales Real Date" />
          </Button>,
      15: <Button rounded={true} className="function-btn" style={styles.darkBtn} executeAction={['cashReport', 'none', 'xml', 'none']}>
            <I18N id="$RESTAURANT_SALES_XML" defaultMessage="Restaurant Sales XML" />
          </Button>,
      16: <Button rounded={true} className="function-btn" style={styles.darkBtn} executeAction={['productMixReportByPeriod', 'RealDate']}>
            <I18N id="$PRODUCT_MIX_REAL_DATE" defaultMessage="Product Mix Real Date" />
          </Button>,
      17: <Button rounded={true} className="function-btn" style={styles.darkBtn} executeAction={['doPrintLogoffReport']}>
            <I18N id="$LOGOFF_REPORT" defaultMessage="Logoff Report" />
          </Button>,
      18: <Button rounded={true} className="function-btn" style={styles.darkBtn} executeAction={['voidedOrdersReport', 'ask', 'RealDate']}>
            <I18N id="$VOIDED_REPORT" defaultMessage="Voided Orders Report" />
          </Button>,
      20: <Button rounded={true} className="function-btn" style={styles.greenBtn} executeAction={['selectTheme', this.availableThemes]}>
            <I18N id="$CHANGE_THEME" defaultMessage="Change Theme" />
          </Button>,
      21: <Button rounded={true} className="function-btn" style={styles.darkBtn} executeAction={['cashReport', 'ask', 'BusinessPeriod']}>
            <I18N id="$RESTAURANT_SALES_Business_Period" defaultMessage="Restaurant Sales Business Period" />
          </Button>,
      22: <Button rounded={true} className="function-btn" style={styles.darkBtn} executeAction={['cashReport', 'current', 'SessionId']}>
            <I18N id="$FLASH_REPORT" defaultMessage="Flash Report" />
          </Button>,
      23: <Button rounded={true} className="function-btn" style={styles.darkBtn} executeAction={['productMixReportByPeriod', 'BusinessPeriod']}>
            <I18N id="$PRODUCT_MIX_BUSINESS_PERIOD" defaultMessage="Product Mix Business Period" />
          </Button>,
      24: <Button rounded={true} className="function-btn" style={styles.darkBtn} executeAction={['hourlySalesReport']}>
            <I18N id="$HOURLY_SALES" defaultMessage="Hourly Sales" />
          </Button>,
      25: <Button rounded={true} className="function-btn" style={styles.darkBtn} executeAction={['speedOfServiceReport']}>
            <I18N id="$SPEEDOFSERVICE" defaultMessage="Speed of Service" />
          </Button>,
      26: <Button rounded={true} className="function-btn" style={styles.darkBtn} executeAction={['salesByBrandReport', 'ask', 'BusinessPeriod']}>
	        <I18N id="$SALESBYBRAND" defaultMessage="Sales by Brand" />
          </Button>,
      27: <Button rounded={true} className="function-btn" style={styles.greenBtn} executeAction={['doCheckUpdates']}>
            <I18N id="$CHECK_UPDATES" defaultMessage="Check for Updates" />
          </Button>
    }

    return (
      <div style={styles.container}>
        <div style={styles.buttonsGroup}>
          <ButtonGrid
            styleCell={styles.gridPadding}
            direction="column"
            cols={4}
            rows={7}
            buttons={buttons}
          />
        </div>
      </div>
    )
  }
}

FunctionScreen.propTypes = {
  /**
   * Order state from `customModelReducer`
   */
  custom: PropTypes.object
}

FunctionScreen.defaultProps = {
  custom: {}
}

function mapStateToProps({ custom }) {
  return {
    custom
  }
}

export default connect(mapStateToProps)(FunctionScreen)
