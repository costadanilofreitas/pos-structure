import _ from 'lodash'
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { FormattedDate } from 'react-intl'
import { I18N } from '3s-posui/core'
import InfoMessage from '3s-posui/widgets/InfoMessage'
import { FlexChild, FlexGrid } from '3s-widgets'
import StaticConfigPropTypes from '../../../../prop-types/StaticConfigPropTypes'
import { getJoinedAvailableSaleTypes, getShortedSaleTypes } from '../../../util/saleTypeConverter'


class DesktopFooterRenderer extends Component {
  constructor(props) {
    super(props)

    this.state = {
      lastClickTime: Date.now()
    }

    this.handleOnFooterClick = this.handleOnFooterClick.bind(this)
  }

  render() {
    const {
      classes, operator, posState, showOperator, showStoreId, showPOSId, showBusinessDate, showVersion, showDrawer,
      drawerState, locale, workingMode, showType, showSaleType, satInfo, remoteOrderStatus, hideInfoMessage,
      staticConfig
    } = this.props
    if (!posState) {
      return <div className={classes.footerRoot}/>
    }

    let formattedSaleTypes
    const joinedSaleTypes = getJoinedAvailableSaleTypes(staticConfig.availableSaleTypes)
    const saleTypes = getShortedSaleTypes(joinedSaleTypes)
    if (showSaleType) {
      formattedSaleTypes = _.join(saleTypes, ' - ')
    }

    const custom = (this.props.custom || {})
    const op = operator || {}
    const { usrCtrlType, podType, posFunction } = workingMode
    const mode = `${usrCtrlType} - ${podType}${posFunction ? ` - ${posFunction}` : ''}`

    const businessDate = new Date()
    businessDate.setFullYear(parseInt(posState.period.substr(0, 4), 10))
    businessDate.setMonth(parseInt(posState.period.substr(4, 2), 10) - 1)
    businessDate.setDate(parseInt(posState.period.substr(6, 2), 10))
    businessDate.setHours(10)

    let localeObj = {
      day: 'numeric',
      month: 'numeric'
    }
    try {
      const dateFormat = new Intl.DateTimeFormat(locale.language)
      localeObj = dateFormat.resolvedOptions()
    } catch (err) {
      console.warn(err)
    }

    const satIsOk = satInfo != null && satInfo.enabled && satInfo.working
    const showCloseSince = !remoteOrderStatus.isOpened && remoteOrderStatus.closedSince != null
    const showLastExternalContact = !remoteOrderStatus.isOnline && remoteOrderStatus.lastExternalContact != null
    const showDeliveryStatus = saleTypes.includes('DL') && staticConfig.remoteOrderStatus.enabled

    return (
      <FlexGrid direction={'row'} onClick={this.handleOnFooterClick}>
        <FlexChild size={11} innerClassName={classes.footerLeftPanel}>
          <FlexGrid direction={'row'}>
            {showOperator &&
            (Object.entries(op).length === 0 || op.stateCode === '4')
              ?
              <FlexChild innerClassName={classes.centerElement} size={6}>
                <span><I18N id="$CLOSED" defaultMessage="Closed"/></span>
              </FlexChild>
              :
              <FlexChild innerClassName={classes.centerElement} size={11}>
                <span className={`${classes.centerElement} ${classes.textElipsis}`}>
                  {op.id} - {op.name.substring(0, 20)}
                </span>
              </FlexChild>
            }
            {showStoreId &&
            <FlexChild innerClassName={classes.centerElement} size={3}>
              <span>&nbsp;{posState.storeId}</span>
            </FlexChild>
            }
            {showPOSId &&
            <FlexChild innerClassName={classes.centerElement} size={3}>
              <span>&nbsp;POS: {posState.id}</span>
            </FlexChild>
            }
            {showType && mode &&
            <FlexChild innerClassName={classes.centerElement} size={6}>
              <span>({mode})</span>
            </FlexChild>
            }
            {showSaleType &&
            <FlexChild innerClassName={classes.centerElement} size={7}>
              <span>({formattedSaleTypes})</span>
            </FlexChild>
            }
            {showBusinessDate &&
            (posState.stateCode !== '0' && posState.stateCode !== '3') &&
            <FlexChild innerClassName={classes.centerElement} size={3}>
              <FormattedDate value={businessDate} day={localeObj.day} month={localeObj.month}/>
            </FlexChild>
            }
            {showVersion &&
            <FlexChild innerClassName={classes.centerElement} size={3}>
              <span>&nbsp;{custom.CODE_VERSION || posState.version}</span>
            </FlexChild>
            }
            {showDrawer &&
            ((!drawerState)
              ?
              <FlexChild innerClassName={classes.centerElement} size={2}>
                <span>&nbsp;<i className="fa fa-lock"/></span>
              </FlexChild>
              :
              <FlexChild innerClassName={classes.centerElement} size={2}>
                <span>&nbsp;<i className="fa fa-unlock"/></span>
              </FlexChild>
            )
            }
            {
              <FlexChild innerClassName={classes.centerElement} size={2}>
                <span>&nbsp;
                  <i className="fas fa-hdd" style={{ color: (satIsOk ? 'green' : 'red') }}/>
                </span>
              </FlexChild>
            }
            {showDeliveryStatus &&
              <FlexChild innerClassName={classes.textCentralize} size={showCloseSince ? 14 : 9}>
                <span>
                  <I18N id="$DELIVERY_STORE"/>&nbsp;
                  {remoteOrderStatus.isOpened
                    ? <span style={{ color: 'green', textTransform: 'uppercase' }}><I18N id="$STORE_OPENED"/></span>
                    : <span style={{ color: 'red', textTransform: 'uppercase' }}><I18N id="$STORE_CLOSED"/></span>
                  }
                  {(showCloseSince &&
                    <span>
                      <I18N id="$SINCE" values={{ 0: remoteOrderStatus.closedSince }}/>
                    </span>
                  )}
                </span>
              </FlexChild>
            }
            {showDeliveryStatus &&
              <FlexChild innerClassName={classes.textCentralize} size={showLastExternalContact ? 15 : 15}>
                <span>
                  <I18N id="$REMOTE_STATUS"/>&nbsp;
                  {remoteOrderStatus.isOnline
                    ? <span style={{ color: 'green', textTransform: 'uppercase' }}><I18N id="$ONLINE"/></span>
                    : <span style={{ color: 'red', textTransform: 'uppercase' }}><I18N id="$OFFLINE"/></span>
                  }
                  {(showLastExternalContact &&
                    <span>
                      <I18N id="$SINCE" values={{ 0: remoteOrderStatus.lastExternalContact }}/>
                    </span>
                  )}
                </span>
              </FlexChild>
            }
          </FlexGrid>
        </FlexChild>
        <FlexChild size={2} outerClassName={classes.footerRightPanel}>
          {!hideInfoMessage && <InfoMessage/>}
        </FlexChild>
      </FlexGrid>
    )
  }

  handleOnFooterClick() {
    if (Date.now() - this.state.lastClickTime < 500) {
      window.location.reload(true)
    }

    this.setState({ lastClickTime: Date.now() })
  }
}

DesktopFooterRenderer.propTypes = {
  classes: PropTypes.object,
  custom: PropTypes.object,
  operator: PropTypes.object,
  posState: PropTypes.object,
  drawerState: PropTypes.bool,
  locale: PropTypes.object,
  workingMode: PropTypes.object,
  showOperator: PropTypes.bool,
  showStoreId: PropTypes.bool,
  showPOSId: PropTypes.bool,
  showType: PropTypes.bool,
  showSaleType: PropTypes.bool,
  showBusinessDate: PropTypes.bool,
  showVersion: PropTypes.bool,
  showDrawer: PropTypes.bool,
  satInfo: PropTypes.object,
  remoteOrderStatus: PropTypes.object,
  hideInfoMessage: PropTypes.bool,
  staticConfig: StaticConfigPropTypes
}

DesktopFooterRenderer.defaultProps = {
  showOperator: true,
  showStoreId: true,
  showPOSId: true,
  showType: true,
  showSaleType: true,
  showBusinessDate: true,
  showVersion: false,
  showDrawer: false,
  workingMode: {},
  satInfo: StaticConfigPropTypes.satInfo,
  remoteOrderStatus: StaticConfigPropTypes.remoteOrderStatus
}

function mapStateToProps({ custom, operator, posState, drawerState, locale, workingMode, satInfo, remoteOrderStatus }) {
  return {
    custom,
    operator,
    posState,
    drawerState,
    locale,
    workingMode,
    satInfo,
    remoteOrderStatus
  }
}

export default connect(mapStateToProps)(DesktopFooterRenderer)
