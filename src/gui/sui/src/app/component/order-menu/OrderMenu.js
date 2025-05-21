import React from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'

import NavigationButton from '../buttons/navigation-button'
import DeviceType from '../../../constants/Devices'
import ButtonGrid from '../button-grid/ButtonGrid'


export default function OrderMenu(
  { selectedMenu, groups, onMenuSelect, themeName, navigationOptions, deviceType, direction, searchNavigation }
) {
  const handleSubmenuClicked = (idx, showBarcodeScreen, showSearchScreen) => () => {
    onMenuSelect(idx, showBarcodeScreen, showSearchScreen)
  }

  function getSubmenu() {
    const subMenuButtons = {}
    let idx = 0
    const mainContainerStyle = { border: 'none', borderRadius: '0', boxShadow: 'none', fontSize: '1.3vmin' }

    _.forEach(groups, (tab) => {
      subMenuButtons[idx] = (
        <NavigationButton
          key={`${idx}_${themeName}`}
          text={tab.button_text}
          code={tab.nav_id}
          mainContainerStyle={mainContainerStyle}
          selected={selectedMenu === idx}
          showSelectionArrow={true}
          showImage={deviceType === DeviceType.Totem}
          textContainerStyle={deviceType === DeviceType.Totem ? { fontSize: '1.5vmin' } : {}}
          onClick={handleSubmenuClicked(idx, false, false)}
        >
        </NavigationButton>
      )
      idx++
    })

    if (navigationOptions.showBarcodeScreen) {
      subMenuButtons[idx] = (
        <NavigationButton
          key={`${idx}_${themeName}`}
          mainContainerStyle={mainContainerStyle}
          showImage={true}
          faIcon={'fa fa-barcode fa-2x'}
          selected={selectedMenu === idx}
          showSelectionArrow={true}
          onClick={handleSubmenuClicked(idx, true, false)}
        >
        </NavigationButton>
      )
      idx++
    }

    if (navigationOptions.showSearchScreen && searchNavigation) {
      subMenuButtons[idx] = (
        <NavigationButton
          key={`${idx}_${themeName}`}
          mainContainerStyle={mainContainerStyle}
          showImage={true}
          faIcon={'fa fa-search fa-2x'}
          selected={selectedMenu === idx}
          showSelectionArrow={true}
          onClick={handleSubmenuClicked(idx, false, true)}
        >
        </NavigationButton>
      )
      idx++
    }

    return subMenuButtons
  }

  const menu = getSubmenu()
  let buttonGrid = <ButtonGrid direction="row" cols={_.size(menu)} rows={1} buttons={menu}/>
  if (direction === 'column') {
    buttonGrid = <ButtonGrid direction="column" cols={1} rows={_.size(menu)} buttons={menu}/>
  }

  return buttonGrid
}

OrderMenu.propTypes = {
  classes: PropTypes.object,
  selectedMenu: PropTypes.number,
  groups: PropTypes.oneOfType([PropTypes.array, PropTypes.object]),
  onMenuSelect: PropTypes.func,
  themeName: PropTypes.string,
  navigationOptions: PropTypes.object,
  deviceType: PropTypes.number,
  direction: PropTypes.string,
  searchNavigation: PropTypes.bool
}

OrderMenu.defaulProps = {
  direction: 'row'
}
