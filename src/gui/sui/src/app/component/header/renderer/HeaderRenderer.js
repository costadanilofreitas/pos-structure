import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'
import { Howl } from 'howler'
import { IconStyle } from '../../../../constants/commonStyles'
import ActionButton from '../../../../component/action-button/'
import Menu from '../../../model/Menu'
import StaticConfigPropTypes from '../../../../prop-types/StaticConfigPropTypes'
import DeliverySound from '../../../../../audio/DeliverySound.mp3'


export default class HeaderRenderer extends Component {
  constructor(props) {
    super(props)
    this.state = {
      deliveryOrderIds: [],
      storedOrdersCount: 0
    }
  }

  componentDidMount() {
    this.notificationSoundPlayer(false)
  }

  componentDidUpdate(prevProps) {
    const { storedOrders } = this.props
    if (prevProps.storedOrders !== storedOrders) {
      this.notificationSoundPlayer(true)
    }
  }

  notificationSoundPlayer(playSound) {
    const { storedOrders, staticConfig } = this.props
    const { deliveryOrderIds } = this.state
    const saleTypes = staticConfig.availableSaleTypes
    const formattedSaleTypes = this.getAllSaleTypes(saleTypes)
    let newOrdersCount = 0
    if (storedOrders) {
      Object.entries(storedOrders).forEach(([key, value]) => {
        if (formattedSaleTypes.includes(key)) {
          newOrdersCount += value
        }
      })
      this.setState({ storedOrdersCount: newOrdersCount })
      let newOrder = false
      for (let i = 0; i < storedOrders.DeliveryIds.length; i++) {
        if (!deliveryOrderIds.includes(storedOrders.DeliveryIds[i])) {
          deliveryOrderIds.push(storedOrders.DeliveryIds[i])
          newOrder = true
          this.setState({ deliveryOrderIds: deliveryOrderIds })
        }
      }
      if (newOrder && staticConfig.deliverySound && playSound) {
        const sound = new Howl({
          src: [DeliverySound],
          volume: 1
        })
        sound.play()
      }
    }
  }

  render() {
    const { classes, selectedMenu, enabledMenus, onMenuClick, staticConfig } = this.props
    const { storedOrdersCount } = this.state
    const saleTypes = staticConfig.availableSaleTypes
    const formattedSaleTypes = this.getAllSaleTypes(saleTypes)
    const displayDesktop = { height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }
    const menuLabel = this.props.mobile ? { display: 'none' } : displayDesktop

    const isOnlyDelivery = saleTypes.length === 1 && saleTypes[0].DELIVERY != null
    const disableButton = !enabledMenus[Menu.RECALL] && classes.disabledColor
    const disableBackground = !enabledMenus[Menu.RECALL] && classes.disabledBackgroundColor

    const headerMenus = [
      <ActionButton
        key={'PANEL'}
        className={'test_Header_PANEL'}
        onClick={enabledMenus[Menu.LOGIN] ? () => onMenuClick(Menu.LOGIN) : null}
        selected={selectedMenu === Menu.LOGIN}
        disabled={!enabledMenus[Menu.LOGIN]}
        inlineText={true}
      >
        <IconStyle
          disabled={!enabledMenus[Menu.LOGIN]}
          className={'icon-style fas fa-user fa-2x'}
          unselected={selectedMenu !== Menu.LOGIN}
        />
        <span style={menuLabel}><I18N id={'$DASHBOARD'}/></span>
      </ActionButton>,
      <ActionButton
        key={'ORDER'}
        className={'test_Header_ORDER'}
        onClick={enabledMenus[Menu.ORDER] ? () => onMenuClick(Menu.ORDER) : null}
        selected={selectedMenu === Menu.ORDER}
        disabled={!enabledMenus[Menu.ORDER]}
        inlineText={true}
      >
        <IconStyle
          disabled={!enabledMenus[Menu.ORDER]}
          className={'icon-style fas fa-shopping-bag fa-2x'}
          unselected={selectedMenu !== Menu.ORDER}
        />
        <span style={menuLabel}><I18N id={'$ORDER'}/></span>
      </ActionButton>,
      <ActionButton
        key={'TABLE'}
        className={'test_Header_TABLE'}
        onClick={enabledMenus[Menu.TABLE] ? () => onMenuClick(Menu.TABLE) : null}
        selected={selectedMenu === Menu.TABLE}
        disabled={!enabledMenus[Menu.TABLE]}
        inlineText={true}
      >
        <IconStyle
          disabled={!enabledMenus[Menu.TABLE]}
          className={'icon-style fas fa-utensils fa-2x'}
          unselected={selectedMenu !== Menu.TABLE}
        />
        <span style={menuLabel}><I18N id={'$TABLE'}/></span>
      </ActionButton>,
      <ActionButton
        key={'RECALL'}
        className={'test_Header_RECALL'}
        onClick={enabledMenus[Menu.RECALL] ? () => onMenuClick(Menu.RECALL) : null}
        selected={selectedMenu === Menu.RECALL}
        disabled={!enabledMenus[Menu.RECALL]}
        inlineText={true}
      >
        <IconStyle
          disabled={!enabledMenus[Menu.RECALL]}
          className={'icon-style fas fa-download fa-2x'}
          unselected={selectedMenu !== Menu.RECALL}
        />
        <span style={menuLabel}>
          {isOnlyDelivery ? <I18N id={'$DELIVERY'}/> : <I18N id={'$RECALL'}/>}
        </span>
        {storedOrdersCount > 0 &&
        <span className={'fa-stack'} style={{ position: 'absolute', top: '0', right: '0', lineHeight: 'unset' }}>
          <span className={`fas fa-shopping-bag ${classes.icon} ${disableButton}` } />
          <span className={`fa-stack-1x ${classes.numberCircle} ${disableBackground}` } style={{ left: 'unset' }} >
            {storedOrdersCount}
          </span>
        </span>}
        {this.props.newMessagesCount > 0 && formattedSaleTypes.includes('DELIVERY') && selectedMenu !== Menu.RECALL &&
        <span className={'fa-stack'} style={{ position: 'absolute', top: '0', left: '0', lineHeight: 'unset' }}>
          <span className={`fas fa-comment ${classes.icon} ${disableButton}` } />
          <span className={`fa-stack-1x ${classes.chatCircle} ${disableBackground}` } style={{ left: 'unset' }} >
            {this.props.newMessagesCount}
          </span>
        </span>}
      </ActionButton>,
      <ActionButton
        key={'OPERATOR'}
        className={'test_Header_OPERATOR'}
        onClick={enabledMenus[Menu.OPERATOR] ? () => onMenuClick(Menu.OPERATOR) : null}
        selected={selectedMenu === Menu.OPERATOR}
        disabled={!enabledMenus[Menu.OPERATOR]}
        inlineText={true}
      >
        <IconStyle
          disabled={!enabledMenus[Menu.OPERATOR]}
          className={'icon-style fas fa-user-tie fa-2x'}
          unselected={selectedMenu !== Menu.OPERATOR}
        />
        <span style={menuLabel}><I18N id={'$OPERATOR'}/></span>
      </ActionButton>,
      <ActionButton
        key={'MANAGER'}
        className={'test_Header_MANAGER-MENU'}
        onClick={enabledMenus[Menu.MANAGER] ? () => onMenuClick(Menu.MANAGER) : null}
        selected={selectedMenu === Menu.MANAGER}
        disabled={!enabledMenus[Menu.MANAGER]}
        inlineText={true}
      >
        <IconStyle
          disabled={!enabledMenus[Menu.MANAGER]}
          className={'icon-style fas fa-tasks fa-2x'}
          unselected={selectedMenu !== Menu.MANAGER}
        />
        <span style={menuLabel}><I18N id={'$MANAGER'}/></span>
      </ActionButton>
    ]

    return (
      <div className={classes.menuItemsContainer}>
        {headerMenus.map((child, index) => <div className={classes.menuItem} key={index}>{child}</div>)}
      </div>
    )
  }

  getAllSaleTypes(saleTypesConfig) {
    let allSaleTypes = []

    for (let i = 0; i < saleTypesConfig.length; i++) {
      allSaleTypes = allSaleTypes.concat(saleTypesConfig[i])
    }

    return allSaleTypes
  }
}

HeaderRenderer.propTypes = {
  selectedMenu: PropTypes.string,
  classes: PropTypes.object,
  mobile: PropTypes.bool,
  onMenuClick: PropTypes.func,
  enabledMenus: PropTypes.object,
  storedOrders: PropTypes.object,
  staticConfig: StaticConfigPropTypes,
  newMessagesCount: PropTypes.number
}
