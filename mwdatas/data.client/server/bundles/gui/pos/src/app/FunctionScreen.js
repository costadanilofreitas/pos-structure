import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import _ from 'lodash'
import { I18N } from 'posui/core'
import { Button } from 'posui/button'
import { ButtonGrid } from 'posui/widgets'
import themes from '../constants/themes'

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
    backgroundColor: '#CDDC39',
    color: '#000'
  },
  blueBtn: {
    backgroundColor: '#002AD6',
    color: '#ffffff'
  },
  purpleBtn: {
    backgroundColor: '#3D007F',
    color: '#ffffff'
  },
  brownBtn: {
    backgroundColor: '#8B542F',
    color: '#ffffff'
  }
}

const FunctionButton = (props) => (
  <Button rounded={true} className="function-btn" blockOnActionRunning={true} {...props}/>
)

export class FunctionScreen extends PureComponent {
  constructor(props) {
    super(props)
    this.availableThemes = _.join(_.map(themes, 'name'), '|')
    this.state = {
      supportScreenOpened: false
    }
  }

  switchServerURL = (serverurl) => {
    if (serverurl) {
      window.location = serverurl
    }
  }

  render() {
    const { custom } = this.props
    const { supportScreenOpened } = this.state
    const { ['Authorization Level']: level = '0', ['POS_FUNCTION']: posFunc = '' } = custom
    // const current = (custom.MIRROR_SCREEN === 'true') ?
    //   <I18N id="$LEFT_HANDED" defaultMessage="Left Handed" /> :
    //   <I18N id="$RIGHT_HANDED" defaultMessage="Right Handed" />
    const mainButtons = {
      0: <FunctionButton style={styles.yellowBtn} executeAction={['doTransfer', '2', 'True']}>
           <I18N id="$SKIM" defaultMessage="Skim" />
         </FunctionButton>,
      1: <FunctionButton style={styles.yellowBtn} executeAction={['doTransfer', '3', 'True']}>
           <I18N id="$CASH_PAID_IN" defaultMessage="Cash Paid In" />
         </FunctionButton>,
      2: <FunctionButton style={styles.yellowBtn} executeAction={['doReportSangria']}>
           <I18N id="$SKIM_REPORT" defaultMessage="Skim Report" />
         </FunctionButton>,
      3: <FunctionButton style={styles.yellowBtn} executeAction={['doVoidSale', 'True', '4', 'True']}>
           <I18N id="$VOID_SALE" defaultMessage="Void Sale" />
         </FunctionButton>,

      5: (Number(level) === 30) ?
        <FunctionButton
          style={styles.yellowBtn}
          onClick={() => this.setState({ supportScreenOpened: true })}
        >
          <I18N id="$SUPPORT_MENU" defaultMessage="Support Menu"/>
        </FunctionButton> : null,
      6: <FunctionButton style={styles.greenBtn} executeAction={['importEmployees']}>
           <I18N id="$UPDATE_USERS" defaultMessage="Update Users" />
         </FunctionButton>,
      7: <FunctionButton style={styles.redBtn} executeAction={['openday', 'false']}>
           <div>
             <I18N id="$OPEN_DAY" defaultMessage="Open Day" />
             <br/>
             (<I18N id="$THIS_POS" defaultMessage="This POS" />)
           </div>
         </FunctionButton>,
      8: <FunctionButton style={styles.redBtn} executeAction={['closeday', 'false']}>
           <div>
             <I18N id="$CLOSE_DAY" defaultMessage="Close Day" />
             <br/>
             (<I18N id="$THIS_POS" defaultMessage="This POS" />)
           </div>
         </FunctionButton>,
      9: <FunctionButton style={styles.redBtn} executeAction={['storewideRestart']}>
           <I18N id="$STOREWIDE_RESTART" defaultMessage="Storewide Restart" />
         </FunctionButton>,
      10: <FunctionButton style={styles.redBtn} executeAction={['doOpenDrawer', 'True']}>
            <I18N id="$OPEN_DRAWER" defaultMessage="Open Drawer" />
          </FunctionButton>,
      12: <FunctionButton style={styles.redBtn} executeAction={['doVoidPaidSale', 'false', 'true', 'true']}>
           <I18N id="$CLOSED_ORDERS" defaultMessage="Closed Orders" />
         </FunctionButton>,
      13: <FunctionButton style={styles.greenBtn} executeAction={['doToggleMirrorScreen']}>
           <I18N id="$MIRROR_SCREEN" defaultMessage="Mirror Screen" />
         </FunctionButton>,
      14: <FunctionButton style={styles.darkBtn} executeAction={['cashReport', 'ask', 'RealDate']}>
            <I18N id="$RESTAURANT_SALES_REAL_DATE" defaultMessage="Restaurant Sales Real Date" />
          </FunctionButton>,
      15: <FunctionButton style={styles.darkBtn} executeAction={['cashReport', 'none', 'xml', 'none']}>
            <I18N id="$RESTAURANT_SALES_XML" defaultMessage="Restaurant Sales XML" />
          </FunctionButton>,
      16: <FunctionButton style={styles.darkBtn} executeAction={['productMixReportByPeriod', 'RealDate']}>
            <I18N id="$PRODUCT_MIX_REAL_DATE" defaultMessage="Product Mix Real Date" />
          </FunctionButton>,
      17: <FunctionButton style={styles.darkBtn} executeAction={['doPrintLogoffReport']}>
            <I18N id="$LOGOFF_REPORT" defaultMessage="Logoff Report" />
          </FunctionButton>,
      18: <FunctionButton style={styles.darkBtn} executeAction={['voidedOrdersReport', 'ask', 'RealDate']}>
            <I18N id="$VOIDED_REPORT" defaultMessage="Voided Orders Report" />
          </FunctionButton>,
      20: <FunctionButton style={styles.greenBtn} executeAction={['selectTheme', this.availableThemes]}>
            <I18N id="$CHANGE_THEME" defaultMessage="Change Theme" />
          </FunctionButton>,
      21: <FunctionButton style={styles.darkBtn} executeAction={['cashReport', 'ask', 'BusinessPeriod']}>
            <I18N id="$RESTAURANT_SALES_Business_Period" defaultMessage="Restaurant Sales Business Period" />
          </FunctionButton>,
      22: <FunctionButton style={styles.darkBtn} executeAction={['cashReport', 'current', 'SessionId']}>
            <I18N id="$FLASH_REPORT" defaultMessage="Flash Report" />
          </FunctionButton>,
      23: <FunctionButton style={styles.darkBtn} executeAction={['productMixReportByPeriod', 'BusinessPeriod']}>
            <I18N id="$PRODUCT_MIX_BUSINESS_PERIOD" defaultMessage="Product Mix Business Period" />
          </FunctionButton>,
      24: <FunctionButton style={styles.darkBtn} executeAction={['hourlySalesReport']}>
            <I18N id="$HOURLY_SALES" defaultMessage="Hourly Sales" />
          </FunctionButton>,
      25: <FunctionButton style={styles.darkBtn} executeAction={['speedOfServiceReport']}>
            <I18N id="$SPEEDOFSERVICE" defaultMessage="Speed of Service" />
          </FunctionButton>,
      26: <FunctionButton style={styles.darkBtn} executeAction={['salesByBrandReport', 'ask', 'BusinessPeriod']}>
            <I18N id="$SALESBYBRAND" defaultMessage="Sales by Brand" />
          </FunctionButton>,
      27: <FunctionButton style={styles.greenBtn} executeAction={['doCheckUpdates']}>
            <I18N id="$CHECK_UPDATES" defaultMessage="Check for Updates" />
          </FunctionButton>
    }

    const supportButtons = {
      0: <FunctionButton style={styles.greenBtn} executeAction={['openday', 'false', 'true']}>
           <div>
             <I18N id="$FORCE_OPEN_DAY" defaultMessage="Force Open Day" />
             <br/>
             (<I18N id="$THIS_POS" defaultMessage="This POS" />)
           </div>
         </FunctionButton>,
      2: <FunctionButton style={styles.blueBtn} executeAction={['doSearchSatModules']}>
           <I18N id="$SAT_STATUS" defaultMessage="SAT Status" />
         </FunctionButton>,
      3: <FunctionButton style={styles.blueBtn} executeAction={['doGetKDSstatus']}>
           <I18N id="$KDS_STATUS" defaultMessage="KDS Status" />
         </FunctionButton>,
      4: <FunctionButton style={styles.blueBtn} executeAction={['doGetPrinterStatus']}>
           <I18N id="$PRINTER_STATUS" defaultMessage="Printer Status" />
         </FunctionButton>,
      5: <FunctionButton style={styles.blueBtn} executeAction={['doCheckSEFAZ']}>
           <I18N id="$SEFAZ_CONNECTION" defaultMessage="SEFAZ Connection" />
         </FunctionButton>,
      6: (posFunc !== 'OT') ?
        <FunctionButton style={styles.blueBtn} executeAction={['doGetSATOperationalStatus']}>
          <I18N id="$SAT_INFO" defaultMessage="SAT Info" />
        </FunctionButton> : null,

      7: <FunctionButton style={styles.purpleBtn} executeAction={['doPurgeKDSs']}>
           <I18N id="$KDS_CLEANUP" defaultMessage="KDS Cleanup" />
         </FunctionButton>,
      8: <FunctionButton style={styles.purpleBtn} executeAction={['doPurgeStoredOrders']}>
           <I18N id="$STORED_ORDERS_CLEANUP" defaultMessage="Stored Orders Cleanup" />
         </FunctionButton>,
      10: <FunctionButton style={styles.blueBtn} executeAction={['doUpdateBlacklist']}>
            <I18N id="$UPDATE_BLACKLIST" defaultMessage="Update Blacklist" />
          </FunctionButton>,
      11: <FunctionButton style={styles.blueBtn} executeAction={['doUpdateVTT']}>
            <I18N id="$UPDATE_VTT" defaultMessage="Update VTT" />
          </FunctionButton>,
      12: <FunctionButton style={styles.blueBtn} executeAction={['doCheckSiTef']}>
            <I18N id="$SITEF_CONNECTION" defaultMessage="SITEF Connection" />
          </FunctionButton>,
      13: <FunctionButton style={styles.blueBtn} executeAction={['doFixPaf']}>
            <I18N id="$EQUALIZE_PAF" defaultMessage="Equalize PAF" />
          </FunctionButton>,

      14: <FunctionButton style={styles.greenBtn} executeAction={['doGetPigeonVersions']}>
            <I18N id="$SOFTWARE_VERSION" defaultMessage="Software Version" />
          </FunctionButton>,
      15: <FunctionButton style={styles.greenBtn} executeAction={['doRecreateXMLFiscal']}>
            <I18N id="$CREATE_FISCAL_XML" defaultMessage="Create Fiscal XML" />
          </FunctionButton>,
      19: <FunctionButton style={styles.greenBtn} executeAction={['doReSignXML']}>
            <I18N id="$RESIGN_XML" defaultMessage="Resign XML" />
          </FunctionButton>,
      20: <FunctionButton style={styles.greenBtn} executeAction={['doFixSefazProtocol']}>
            <I18N id="$FIX_SEFAZ_PROTOCOL" defaultMessage="Fix SEFAZ Protocol" />
          </FunctionButton>,

      21: (posFunc !== 'OT') ?
        <FunctionButton style={styles.redBtn} executeAction={['doKill']}>
          <I18N id="$CLOSE_APPLICATION" defaultMessage="Close Application" />
        </FunctionButton> : null,
      22: <FunctionButton style={styles.blueBtn} executeAction={['doSyncDeliveryMenu']}>
            <I18N id="$SYNC_DELIVERY_MENU" defaultMessage="Sync Delivery Menu" />
          </FunctionButton>,
      23: <FunctionButton style={styles.blueBtn} executeAction={['doRuptureCleanup']}>
            <I18N id="$RUPTURE_CLEANUP" defaultMessage="Rupture Cleanup" />
          </FunctionButton>,
      24: <FunctionButton style={styles.yellowBtn} executeAction={['changeRemoteOrderStoreStatus']}>
            <I18N id="$CHANGE_REMOTE_STORE_STATUS" defaultMessage="Change Remote Order Status" />
          </FunctionButton>,
      27: <FunctionButton
            style={styles.brownBtn}
            onClick={() => this.setState({ supportScreenOpened: false })}
          >
            <I18N id="$BACK" defaultMessage="Back" />
          </FunctionButton>
    }

    return (
      <div style={styles.container}>
        <div style={styles.buttonsGroup}>
          <ButtonGrid
            styleCell={styles.gridPadding}
            direction="column"
            cols={4}
            rows={7}
            buttons={supportScreenOpened ? supportButtons : mainButtons}
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
