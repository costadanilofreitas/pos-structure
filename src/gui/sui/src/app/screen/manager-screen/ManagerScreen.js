import React, { PureComponent } from 'react'
import { connect } from 'react-redux'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'

import withState from '../../../util/withState'
import WorkingModePropTypes from '../../../prop-types/WorkingModePropTypes'
import { isLoginQS, isLoginTS, isFrontPod } from '../../model/modelHelper'
import withStaticConfig from '../../util/withStaticConfig'
import StaticConfigPropTypes from '../../../prop-types/StaticConfigPropTypes'
import Button from '../../../component/action-button/Button'
import { CURRENT_THEME_CHANGED } from '../../../constants/actionTypes'
import DialogType from '../../../constants/DialogType'
import withShowDialog from '../../../util/withShowDialog'
import ButtonGrid from '../../component/button-grid/ButtonGrid'


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
    margin: '0.5vw',
    background: 'rgb(255, 255, 255)'
  },
  gridPadding: {
    padding: '1px'
  },
  purpleBtn: {
    backgroundColor: '#5E3A8D',
    color: '#ffffff'
  },
  pinkBtn: {
    backgroundColor: '#FF3D72',
    color: '#ffffff'
  },
  greenBtn: {
    backgroundColor: '#49CDA2',
    color: '#ffffff'
  },
  blueBtn: {
    backgroundColor: '#3D73CC',
    color: '#ffffff'
  }
}

const FunctionButton = (props) => (
  <Button blockOnActionRunning {...props}/>
)

export class ManagerScreen extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      supportScreenOpened: false,
      userScreenOpened: false
    }

    this.onThemeChanged = this.onThemeChanged.bind(this)
  }

  getMenuManagerButtons() {
    const {
      workingMode,
      operator,
      custom,
      staticConfig: { showCashInAndCashOut }
    } = this.props

    const level = custom != null ? custom['Authorization Level'] : '0'
    const operatorId = operator == null ? '' : operator.id

    return {
      0: (showCashInAndCashOut) &&
        <FunctionButton
          className={'test_ManagerScreen_SKIM'}
          style={styles.purpleBtn}
          executeAction={['do_transfer', '4', operatorId, isLoginQS(workingMode)]}
        >
          <I18N id="$SKIM" defaultMessage="Skim"/>
        </FunctionButton>,

      1: (showCashInAndCashOut) &&
        <FunctionButton
          className={'test_ManagerScreen_CASH-PAID-IN'}
          style={styles.purpleBtn}
          executeAction={['do_transfer', '3', operatorId, isLoginQS(workingMode)]}
        >
          <I18N id="$CASH_PAID_IN" defaultMessage="Cash Paid In"/>
        </FunctionButton>,

      2: (showCashInAndCashOut) &&
        <FunctionButton
          className={'test_ManagerScreen_TRANSFERS-REPORT'}
          style={styles.purpleBtn}
          executeAction={['transfers_report']}
        >
          <I18N id="$TRANSFERS_REPORT"/>
        </FunctionButton>,

      3:
        <FunctionButton
          className={'test_ManagerScreen_VOID-SALE'}
          style={styles.purpleBtn}
          executeAction={['do_void_order', '4', 'True']}
        >
          <I18N id="$VOID_SALE" defaultMessage="Void Last Sale"/>
        </FunctionButton>,

      4:
        <FunctionButton
          className={'test_ManagerScreen_MANAGE-SPECIAL-CATALOGS'}
          style={styles.purpleBtn}
          executeAction={['doSpecialCatalog']}
        >
          <I18N id="$MANAGE_SPECIAL_CATALOGS" defaultMessage="Manage Special Catalogs"/>
        </FunctionButton>,

      5:
        <FunctionButton
          className={'test_ManagerScreen_RUPTURE'}
          style={styles.purpleBtn}
          executeAction={['open_rupture']}
        >
          <I18N id="$ITEMS_RUPTURE" defaultMessage="Items Rupture"/>
        </FunctionButton>,

      6: (Number(level) >= 20)
        ?
        <FunctionButton
          className={'test_ManagerScreen_SUPPORT-MENU'}
          style={styles.greenBtn}
          onClick={() => this.setState({ supportScreenOpened: true })}
        >
          <I18N id="$SUPPORT_MENU" defaultMessage="Support Menu"/>
        </FunctionButton>
        : null,

      7: (isLoginQS(workingMode)) ?
        <FunctionButton
          className={'test_ManagerScreen_OPEN-DAY'}
          style={styles.pinkBtn}
          executeAction={['openday', 'false']}
        >
          <div>
            <I18N id="$OPEN_DAY" defaultMessage="Open Day"/>
            <br/>
            (<I18N id="$THIS_POS" defaultMessage="This POS"/>)
          </div>
        </FunctionButton> :
        <FunctionButton
          className={'test_ManagerScreen_OPEN-DAY'}
          style={styles.pinkBtn}
          executeAction={['open_day']}
        >
          <div>
            <I18N id="$OPEN_DAY" defaultMessage="Open Day"/>
            <br/>
            (<I18N id="$STORE_WIDE" defaultMessage="Store Wide"/>)
          </div>
        </FunctionButton>,

      8:
        <FunctionButton
          className={'test_ManagerScreen_CLOSE-DAY'}
          style={styles.pinkBtn}
          executeAction={['close_day']}
        >
          <div>
            <I18N id="$CLOSE_DAY" defaultMessage="Close Day"/>
            <br/>
            (<I18N id="$THIS_POS" defaultMessage="This POS"/>)
          </div>
        </FunctionButton>,

      9:
        <FunctionButton
          className={'test_ManagerScreen_CLOSE-OPERATORS'}
          style={styles.pinkBtn}
          executeAction={['close_operators']}
        >
          <I18N id="$CLOSE_OPERATORS"/>
        </FunctionButton>,

      10:
        <FunctionButton
          className={'test_ManagerScreen_STOREWIDE-RESTART'}
          style={styles.pinkBtn}
          executeAction={['storewideRestart']}
        >
          <I18N id="$STOREWIDE_RESTART" defaultMessage="Storewide Restart"/>
        </FunctionButton>,

      11:
        <FunctionButton
          className={'test_ManagerScreen_OPEN-DRAWER'}
          style={styles.pinkBtn}
          executeAction={['doOpenDrawer', 'True']}
        >
          <I18N id="$OPEN_DRAWER" defaultMessage="Open Drawer"/>
        </FunctionButton>,

      12: (isLoginQS(workingMode))
        ?
        <FunctionButton
          className={'test_ManagerScreen_CLOSED-ORDERS'}
          style={styles.pinkBtn}
          executeAction={['closedOrders', 'false', 'true', 'true', '', 'QSR']}
        >
          <I18N id="$CLOSED_ORDERS" defaultMessage="Closed Orders"/>
        </FunctionButton>
        :
        <FunctionButton
          className={'test_ManagerScreen_CLOSED-ORDERS'}
          style={styles.pinkBtn}
          executeAction={['closedOrders', 'false', 'true', 'true', '', 'TS']}
        >
          <I18N id="$CLOSED_ORDERS" defaultMessage="Closed Orders"/>
        </FunctionButton>,

      13:
        <FunctionButton
          className={'test_ManagerScreen_UPDATE-USERS'}
          style={styles.greenBtn}
          executeAction={['update_users']}
        >
          <I18N id="$UPDATE_USERS" defaultMessage="Update Users"/>
        </FunctionButton>,

      14:
        <FunctionButton
          className={'test_ManagerScreen_SALES-REPORT-BY-BUSINESS-PERIOD'}
          style={styles.blueBtn}
          executeAction={['cashReport', 'ask', 'BusinessPeriod', 'notAsk', 'True']}
        >
          <I18N id="$RESTAURANT_SALES_BUSINESS_PERIOD"/>
        </FunctionButton>,

      15:
        <FunctionButton
          className={'test_ManagerScreen_INTERVAL-SALES'}
          style={styles.blueBtn}
          executeAction={['hourlySalesReport', 'ask', 'ask', 'False']}
        >
          <I18N id="$INTERVAL_SALES"/>
        </FunctionButton>,

      16: (isFrontPod(workingMode))
        ?
        <FunctionButton
          className={'SPEED-OF-SERVICE'}
          style={styles.blueBtn}
          executeAction={['speedOfServiceReport']}
        >
          <I18N id="$SPEEDOFSERVICE" defaultMessage="Speed of Service"/>
        </FunctionButton>
        :
        <FunctionButton
          className={'test_ManagerScreen_OPENED-TABLES'}
          style={styles.blueBtn}
          executeAction={['opened_tables_report']}
        >
          <I18N id="$OPENED_TABLES"/>
        </FunctionButton>,

      17:
        <FunctionButton
          className={'test_ManagerScreen_DAILY-GOALS'}
          style={styles.blueBtn}
          executeAction={['show_daily_goals', '', 'True', 'True', 'True', 'True']}
        >
          <I18N id="$DAILY_GOALS"/>
        </FunctionButton>,

      20:
        <FunctionButton
          className={'test_ManagerScreen_CHECK-UPDATES'}
          style={styles.greenBtn}
          executeAction={['update_menu']}
        >
          <I18N id="$MENU_UPDATE"/>
        </FunctionButton>,

      21:
        <FunctionButton
          className={'test_ManagerScreen_SALES-REAL-DATE'}
          style={styles.blueBtn}
          executeAction={['cashReport', 'ask', 'RealDate', 'notAsk', 'True']}
        >
          <I18N id="$RESTAURANT_SALES_REAL_DATE"/>
        </FunctionButton>,

      22:
        <FunctionButton
          className={'test_ManagerScreen_VOIDED-LINES-REPORT'}
          style={styles.blueBtn}
          executeAction={['get_voided_lines_report']}
        >
          <I18N id="$VOIDED_LINES_REPORT" defaultMessage="Voided Lines Report"/>
        </FunctionButton>,

      23: (isLoginTS(workingMode))
        ?
        <FunctionButton
          className={'test_ManagerScreen_TIP-REPORT'}
          style={styles.blueBtn}
          executeAction={['tipReport']}
        >
          <I18N id="$TIP_REPORT" defaultMessage="Tip Report"/>
        </FunctionButton>
        :
        <FunctionButton
          className={'test_ManagerScreen_LOGOFF-REPORT'}
          style={styles.blueBtn}
          executeAction={['doPrintLogoffReport']}
        >
          <I18N id="$LOGOFF_REPORT" defaultMessage="Logoff Report"/>
        </FunctionButton>,

      24: (isLoginQS(workingMode))
        ?
        <FunctionButton
          className={'test_ManagerScreen_SESSION-ID-REPORT'}
          style={styles.blueBtn}
          executeAction={['cashReport', 'current', 'SessionId', 'current', 'False']}
        >
          <I18N id="$SESSION_ID_REPORT"/>
        </FunctionButton>
        : null,

      25:
        <FunctionButton
          className={'test_ManagerScreen_DISCOUNT-REPORT'}
          style={styles.blueBtn}
          executeAction={['discountReport', '', 'BusinessPeriod', 'notAsk', 'True']}
        >
          <I18N id="$DISCOUNT_REPORT"/>
        </FunctionButton>,

      27:
        <FunctionButton
          className={'function-btn test_ManagerScreen_MEDIA-UPDATE'}
          style={styles.greenBtn}
          executeAction={['update_media']}
        >
          <I18N id="$MEDIA_UPDATE" defaultMessage="Update Media"/>
        </FunctionButton>,

      28:
        <FunctionButton
          className={'test_ManagerScreen_MIX-BUSINESS'}
          style={styles.blueBtn}
          executeAction={['productMixReportByPeriod', 'BusinessPeriod', 'notAsk', 'ask']}
        >
          <I18N id="$PRODUCT_MIX_BUSINESS_PERIOD" defaultMessage="Product Mix Real Date"/>
        </FunctionButton>,

      29:
        <FunctionButton
          className={'test_ManagerScreen_VOIDED-REPORT'}
          style={styles.blueBtn}
          executeAction={['voidedOrdersReport', 'ask', 'BusinessPeriod']}
        >
          <I18N id="$VOIDED_REPORT" defaultMessage="Voided Orders Report"/>
        </FunctionButton>,

      30:
        <FunctionButton
          className={'test_ManagerScreen_SALES-BY-BRAND'}
          style={styles.blueBtn}
          executeAction={['cashReport', 'ask', 'BusinessPeriod', 'ask', 'True', '', 'False', 'False', 'True']}
        >
          <I18N id="$SALESBYBRAND" defaultMessage="Sales by Brand"/>
        </FunctionButton>,

      31:
        <FunctionButton
          className={'test_ManagerScreen_DELIVERY-REPORT'}
          style={styles.blueBtn}
          executeAction={['do_delivery_report']}
        >
          <I18N id="$REPORT_DELIVERY" defaultMessage="Delivery Report"/>
        </FunctionButton>,

      32:
        <FunctionButton
          className={'test_ManagerScreen_OPERATOR-CLOSING'}
          style={styles.blueBtn}
          executeAction={['show_operator_closing', '', '']}
        >
          <I18N id="$OPERATOR_CLOSING"/>
        </FunctionButton>,

      34:
        <FunctionButton
          className={'test_ManagerScreen_DELIVERY-CONTROL'}
          style={styles.greenBtn}
          executeAction={['delivery_control_button']}
        >
          <I18N id="$DELIVERY_CONTROL" defaultMessage="Delivery Control"/>
        </FunctionButton>
    }
  }

  getSupportMenuButtons() {
    const { custom } = this.props
    const posFunc = custom != null ? custom.POS_FUNCTION : ''

    return {
      0:
        <FunctionButton
          className={'test_ManagerScreen_FORCE-OPEN-DAY'}
          style={styles.greenBtn}
          executeAction={['openday', 'false', 'true']}
        >
          <div>
            <I18N id="$FORCE_OPEN_DAY" defaultMessage="Force Open Day"/>
            <br/>
            (<I18N id="$THIS_POS" defaultMessage="This POS"/>)
          </div>
        </FunctionButton>,
      2:
        <FunctionButton
          className={'test_ManagerScreen_SAT-STATUS'}
          style={styles.blueBtn}
          executeAction={['doSearchSatModules']}
        >
          <I18N id="$SAT_STATUS" defaultMessage="SAT Status"/>
        </FunctionButton>,
      3:
        <FunctionButton
          className={'test_ManagerScreen_KDS-STATUS'}
          style={styles.blueBtn}
          executeAction={['doGetKDSstatus']}
        >
          <I18N id="$KDS_STATUS" defaultMessage="KDS Status"/>
        </FunctionButton>,
      4:
        <FunctionButton
          className={'test_ManagerScreen_PRINTER-STATUS'}
          style={styles.blueBtn}
          executeAction={['doGetPrinterStatus']}
        >
          <I18N id="$PRINTER_STATUS" defaultMessage="Printer Status"/>
        </FunctionButton>,
      5:
        <FunctionButton
          className={'test_ManagerScreen_SEFAZ-CONNECTION'}
          style={styles.blueBtn}
          executeAction={['doCheckSEFAZ']}
        >
          <I18N id="$SEFAZ_CONNECTION" defaultMessage="SEFAZ Connection"/>
        </FunctionButton>,
      6: (posFunc !== 'OT') ?
        <FunctionButton
          className={'test_ManagerScreen_SAT-INFO'}
          style={styles.blueBtn}
          executeAction={['get_sat_status']}
        >
          <I18N id="$SAT_INFO" defaultMessage="SAT Info"/>
        </FunctionButton> : null,
      7:
        <FunctionButton
          className={'test_ManagerScreen_KDS-CLEANUP'}
          style={styles.purpleBtn}
          executeAction={['purge_kds_orders']}
        >
          <I18N id="$KDS_CLEANUP" defaultMessage="KDS Cleanup"/>
        </FunctionButton>,
      8:
        <FunctionButton
          className={'test_ManagerScreen_STORED-ORDERS-CLEANUP'}
          style={styles.purpleBtn}
          executeAction={['doPurgeStoredOrders']}
        >
          <I18N id="$STORED_ORDERS_CLEANUP" defaultMessage="Stored Orders Cleanup"/>
        </FunctionButton>,
      10:
        <FunctionButton
          className={'test_ManagerScreen_UPDATE-BLACKLIST'}
          style={styles.blueBtn}
          executeAction={['doUpdateBlacklist']}
        >
          <I18N id="$UPDATE_BLACKLIST" defaultMessage="Update Blacklist"/>
        </FunctionButton>,
      11:
        <FunctionButton
          className={'test_ManagerScreen_UPDATE-VTT'}
          style={styles.blueBtn}
          executeAction={['doUpdateVTT']}
        >
          <I18N id="$UPDATE_VTT" defaultMessage="Update VTT"/>
        </FunctionButton>,
      12:
        <FunctionButton
          className={'test_ManagerScreen_SITEF-CONNECTION'}
          style={styles.blueBtn}
          executeAction={['doCheckSiTef']}
        >
          <I18N id="$SITEF_CONNECTION" defaultMessage="SITEF Connection"/>
        </FunctionButton>,
      13:
        <FunctionButton
          className={'test_ManagerScreen_EQUALIZE-PAF'}
          style={styles.blueBtn}
          executeAction={['doFixPaf']}
        >
          <I18N id="$EQUALIZE_PAF" defaultMessage="Equalize PAF"/>
        </FunctionButton>,
      14:
        <FunctionButton
          className={'test_ManagerScreen_SOFTWARE-VERSION'}
          style={styles.greenBtn}
          executeAction={['doGetPigeonVersions']}
        >
          <I18N id="$SOFTWARE_VERSION" defaultMessage="Software Version"/>
        </FunctionButton>,
      15:
        <FunctionButton
          className={'test_ManagerScreen_CREATE-FISCAL-XML'}
          style={styles.greenBtn}
          executeAction={['doRecreateXMLFiscal']}
        >
          <I18N id="$CREATE_FISCAL_XML" defaultMessage="Create Fiscal XML"/>
        </FunctionButton>,
      16:
        <FunctionButton
          className={'test_ManagerScreen_SALES-XML'}
          style={styles.blueBtn}
          executeAction={['cashReport', 'none', 'xml', 'none']}
        >
          <I18N id="$RESTAURANT_SALES_XML" defaultMessage="Restaurant Sales"/>
        </FunctionButton>,
      19:
        <FunctionButton
          className={'test_ManagerScreen_RESIGN-XML'}
          style={styles.greenBtn}
          executeAction={['doReSignXML']}
        >
          <I18N id="$RESIGN_XML" defaultMessage="Resign XML"/>
        </FunctionButton>,
      20:
        <FunctionButton
          className={'test_ManagerScreen_FIX-SEFAZ-PROTOCOL'}
          style={styles.greenBtn}
          executeAction={['doFixSefazProtocol']}
        >
          <I18N id="$FIX_SEFAZ_PROTOCOL" defaultMessage="Fix SEFAZ Protocol"/>
        </FunctionButton>,
      21: (posFunc !== 'OT') ?
        <FunctionButton
          className={'test_ManagerScreen_CLOSE-APPLICATION'}
          style={styles.pinkBtn}
          executeAction={['doKill']}
        >
          <I18N id="$CLOSE_APPLICATION" defaultMessage="Close Application"/>
        </FunctionButton> : null,
      22:
        <FunctionButton
          className={'test_ManagerScreen_SYNC-DELIVERY-MENU'}
          style={styles.blueBtn}
          executeAction={['doSyncDeliveryMenu']}
        >
          <I18N id="$SYNC_DELIVERY_MENU" defaultMessage="Sync Delivery Menu"/>
        </FunctionButton>,
      23:
        <FunctionButton
          className={'test_ManagerScreen_RUPTURE-CLEANUP'}
          style={styles.blueBtn}
          executeAction={['doRuptureCleanup']}
        >
          <I18N id="$RUPTURE_CLEANUP" defaultMessage="Rupture Cleanup"/>
        </FunctionButton>,
      24:
        <FunctionButton
          className={'test_ManagerScreen_CHANGE-USERS'}
          onClick={() => this.setState({ supportScreenOpened: false, userScreenOpened: true })}
        >
          <I18N id="$CHANGE_USERS" defaultMessage="Change Users Data"/>
        </FunctionButton>,
      28:
        <FunctionButton
          className={'test_ManagerScreen_UPDATE_LOADERS'}
          style={styles.purpleBtn}
          executeAction={['update_loaders']}
        >
          <I18N id="$UPDATE_LOADERS" defaultMessage="Update Loaders"/>
        </FunctionButton>,
      34:
        <FunctionButton
          className={'test_ManagerScreen_BACK'}
          onClick={() => this.setState({ supportScreenOpened: false })}
        >
          <I18N id="$BACK" defaultMessage="Back"/>
        </FunctionButton>
    }
  }

  getUserMenuButtons() {
    return {
      0:
        <FunctionButton
          className={'test_ManagerScreen_CHANGE-PASSWORD'}
          style={styles.blueBtn}
          executeAction={['change_user_password']}
        >
          <I18N id="$CHANGE_PASSWORD" defaultMessage="Change Password"/>
        </FunctionButton>,
      1:
        <FunctionButton
          className={'test_ManagerScreen_CREATE-USER'}
          style={styles.blueBtn}
          executeAction={['createuser']}
        >
          <I18N id="$CREATE_USER" defaultMessage="Create User"/>
        </FunctionButton>,
      2:
        <FunctionButton
          className={'test_ManagerScreen_REMOVE-USER'}
          style={styles.blueBtn}
          executeAction={['removeuser']}
        >
          <I18N id="$REMOVE_USER" defaultMessage="Remove User"/>
        </FunctionButton>,
      3:
        <FunctionButton
          className={'test_ManagerScreen_INACTIVATE-USER'}
          style={styles.blueBtn}
          executeAction={['inactivateuser']}
        >
          <I18N id="$INACTIVATE_USER" defaultMessage="Inactivate User"/>
        </FunctionButton>,
      4:
        <FunctionButton
          className={'test_ManagerScreen_ACTIVATE-USER'}
          style={styles.blueBtn}
          executeAction={['activateuser']}
        >
          <I18N id="$ACTIVATE_USER" defaultMessage="Activate User"/>
        </FunctionButton>,
      5:
        <FunctionButton
          className={'test_ManagerScreen_CHANGE-PROFILE'}
          style={styles.blueBtn}
          executeAction={['changeperfil']}
        >
          <I18N id="$CHANGE_PROFILE" defaultMessage="Change User Profile"/>
        </FunctionButton>,
      6:
        <FunctionButton
          className={'test_ManagerScreen_LIST-USERS'}
          style={styles.blueBtn}
          executeAction={['list_all_users']}
        >
          <I18N id="$LIST_ALL_USERS" defaultMessage="List All Users"/>
        </FunctionButton>,
      27:
        <FunctionButton
          className={'test_ManagerScreen_BACK'}
          onClick={() => this.setState({ userScreenOpened: false, supportScreenOpened: true })}
        >
          <I18N id="$BACK" defaultMessage="Back"/>
        </FunctionButton>
    }
  }

  render() {
    const { supportScreenOpened: supportButtonsOpened, userScreenOpened: userButtonsOpened } = this.state

    const menuManagerButtons = this.getMenuManagerButtons()
    const supportMenuButtons = this.getSupportMenuButtons()
    const usersMenuButtons = this.getUserMenuButtons()

    let currentButtons

    if (supportButtonsOpened) {
      currentButtons = supportMenuButtons
    } else if (userButtonsOpened) {
      currentButtons = usersMenuButtons
    } else {
      currentButtons = menuManagerButtons
    }

    return (
      <div style={styles.container}>
        <div style={styles.buttonsGroup}>
          <ButtonGrid
            styleCell={styles.gridPadding}
            direction="column"
            cols={5}
            rows={7}
            buttons={currentButtons}
          />
        </div>
      </div>)
  }

  changeTheme() {
    const { showDialog } = this.props
    const themes = this.getThemesNames()

    showDialog({
      title: '$WARNING',
      type: DialogType.List,
      list: themes,
      message: '$DEVICE_NOT_INITIALIZED',
      onClose: this.onThemeChanged
    })
  }

  onThemeChanged(themeIndex) {
    const { dispatchNewTheme } = this.props
    const themes = this.getThemesNames()

    dispatchNewTheme(themes[themeIndex])
  }

  getThemesNames() {
    return this.props.theme.themes.map(a => a.name)
  }
}

ManagerScreen.propTypes = {
  custom: PropTypes.object,
  workingMode: WorkingModePropTypes,
  operator: PropTypes.object,
  showCashInAndCashOut: PropTypes.bool,
  staticConfig: StaticConfigPropTypes,
  dispatchNewTheme: PropTypes.func,
  showDialog: PropTypes.func,
  theme: PropTypes.object
}

ManagerScreen.defaultProps = {
  custom: {}
}

function mapDispatchToProps(dispatch) {
  return {
    dispatchNewTheme: function (newTheme) {
      dispatch({ type: CURRENT_THEME_CHANGED, payload: newTheme })
    }
  }
}

export default withShowDialog(withStaticConfig(withState(
  connect(null, mapDispatchToProps)(ManagerScreen), 'custom', 'workingMode', 'operator', 'theme')))
