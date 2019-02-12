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
      0: <Button rounded={true} className="function-btn" style={styles.yellowBtn} executeAction={['doWasteRefundTransaction', 'refund']}>
           <I18N id="$ISSUE_REFUND" defaultMessage="Issue Refund" />
         </Button>,
      1: <Button rounded={true} className="function-btn" style={styles.yellowBtn} executeAction={['doPrintOpenChecks']}>
           <I18N id="$PRINT_OPEN_CHECKS" defaultMessage="Print Open Checks" />
         </Button>,
      2: <Button rounded={true} className="function-btn" style={styles.yellowBtn} executeAction={['importEmployees']}>
           <I18N id="$UPDATE_USERS" defaultMessage="Update Users" />
         </Button>,
      3: <Button rounded={true} className="function-btn" style={styles.yellowBtn} executeAction={['doTransfer', '2', 'True']}>
           <I18N id="$SKIM" defaultMessage="Skim" />
         </Button>,
      4: <Button rounded={true} className="function-btn" style={styles.yellowBtn} executeAction={['doTransfer', '3', 'True']}>
           <I18N id="$CASH_PAID_IN" defaultMessage="Cash Paid In" />
         </Button>,
      5: <Button rounded={true} className="function-btn" style={styles.yellowBtn} executeAction={['doTransfer', '4', 'True']}>
           <I18N id="$CASH_PAID_OUT" defaultMessage="Cash Paid Out" />
         </Button>,
      7: <Button rounded={true} className="function-btn" style={styles.redBtn} executeAction={['openday', 'true']}>
           <div>
             <I18N id="$OPEN_DAY" defaultMessage="Open Day" />
             <br/>
             (<I18N id="$STORE_WIDE" defaultMessage="Store Wide" />)
           </div>
         </Button>,
      8: <Button rounded={true} className="function-btn" style={styles.redBtn} executeAction={['closeday', 'true']}>
           <div>
             <I18N id="$CLOSE_DAY" defaultMessage="Close Day" />
             <br/>
             (<I18N id="$STORE_WIDE" defaultMessage="Store Wide" />)
           </div>
         </Button>,
      9: <Button rounded={true} className="function-btn" style={styles.redBtn} executeAction={['doVoidPaidSale', 'false', 'true', 'true']}>
           <I18N id="$CLOSED_ORDERS" defaultMessage="Closed Orders" />
         </Button>,
      11: <Button rounded={true} className="function-btn" style={styles.redBtn} executeAction={['doUpdateMediaData']}>
            <I18N id="$MEDIA_UPDATE" defaultMessage="Update Media" />
          </Button>,
      14: <Button rounded={true} className="function-btn" style={styles.redBtn} executeAction={['openday', 'false']}>
            <div>
              <I18N id="$OPEN_DAY" defaultMessage="Open Day" />
              <br/>
              (<I18N id="$THIS_POS" defaultMessage="This POS" />)
            </div>
          </Button>,
      15: <Button rounded={true} className="function-btn" style={styles.redBtn} executeAction={['closeday', 'false']}>
            <div>
              <I18N id="$CLOSE_DAY" defaultMessage="Close Day" />
              <br/>
              (<I18N id="$THIS_POS" defaultMessage="This POS" />)
            </div>
          </Button>,
      16: <Button rounded={true} className="function-btn" style={styles.redBtn} executeAction={['storewideRestart']}>
            <I18N id="$STOREWIDE_RESTART" defaultMessage="Storewide Restart" />
          </Button>,
      17: <Button rounded={true} className="function-btn" style={styles.redBtn} executeAction={['doOpenDrawer', 'True']}>
            <I18N id="$OPEN_DRAWER" defaultMessage="Open Drawer" />
          </Button>,
      18: <Button rounded={true} className="function-btn" style={styles.redBtn} executeAction={['doCheckUpdates']}>
            <I18N id="$CHECK_UPDATES" defaultMessage="Check for Updates" />
          </Button>,
      20: <Button rounded={true} className="function-btn" style={styles.greenBtn} executeAction={['selectTheme', this.availableThemes]}>
            <I18N id="$CHANGE_THEME" defaultMessage="Change Theme" />
          </Button>,
      21: <Button rounded={true} className="function-btn" style={styles.darkBtn} executeAction={['cashReport', 'end_of_day', 'True']}>
            <I18N id="$RESTAURANT_SALES" defaultMessage="Restaurant Sales" />
          </Button>,
      22: <Button rounded={true} className="function-btn" style={styles.darkBtn} executeAction={['cashReport']}>
            <I18N id="$FLASH_REPORT" defaultMessage="Flash Report" />
          </Button>,
      23: <Button rounded={true} className="function-btn" style={styles.darkBtn} executeAction={['laborReport']}>
            <I18N id="$LABOR_REPORT" defaultMessage="Labor Report" />
          </Button>,
      24: <Button rounded={true} className="function-btn" style={styles.darkBtn} executeAction={['productMixReport']}>
            <I18N id="$PRODUCT_MIX" defaultMessage="Product Mix" />
          </Button>,
      25: <Button rounded={true} className="function-btn" style={styles.darkBtn} executeAction={['hourlySalesReport']}>
            <I18N id="$HOURLY_SALES" defaultMessage="Hourly Sales" />
          </Button>,
      26: <Button rounded={true} className="function-btn" style={styles.greenBtn} executeAction={['doToggleMirrorScreen']}>
            <div>
              <I18N id="$FLIP_SCREEN" defaultMessage="Flip Screen" />
              <br/>
              <I18N id="$CURRENT_VALUE" defaultMessage="Current: {0}" values={{ 0: current }} />
            </div>
          </Button>,
      27: <Button rounded={true} className="function-btn" style={styles.greenBtn} executeAction={['doChangeLanguage']}>
            <I18N id="$CHANGE_LANGUAGE" defaultMessage="Change Language" />
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
