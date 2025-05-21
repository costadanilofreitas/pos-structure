import React from 'react'
import PropTypes from 'prop-types'
import includes from 'lodash/includes'
import flatten from 'lodash/flatten'
import _find from 'lodash/find'

import { I18N } from '3s-posui/core'

import ActionButton from '../../../../component/action-button'
import { ButtonContainer } from './styles'
import ScreenOrientation from '../../../../constants/ScreenOrientation'


function isInAllSaleTypes(allSaleTypes, saleType) {
  return includes(flatten(allSaleTypes), saleType)
}

function disableButton(allSaleTypes, saleType, buttonSaleType) {
  const allowedSaleTypes = _find(allSaleTypes, (types) => includes(types, saleType))
  return !includes(allowedSaleTypes, buttonSaleType)
}

export default function TotemSaleTypeRenderer(
  { saleType, onSaleTypeClick, availableSaleTypes, order, screenOrientation }
) {
  const allSaleTypes = _.isEmpty(availableSaleTypes) ? [['EAT_IN']] : availableSaleTypes

  const firstAvailableSaleType = allSaleTypes[0][0]
  const selectedSaleType = isInAllSaleTypes(allSaleTypes, saleType) ? saleType : firstAvailableSaleType
  const orderIsInProgress = order.state === 'IN_PROGRESS'

  const buttonsProps = [
    {
      name: 'EAT_IN',
      className: 'test_SaleType_EAT-IN',
      i18nCode: '$KIOSK_EAT_IN',
      icon: 'fas fa-hamburger'
    },
    {
      name: 'TAKE_OUT',
      className: 'test_SaleType_TAKE-OUT',
      i18nCode: '$KIOSK_TAKE_OUT',
      icon: 'fas fa-shopping-bag'
    },
    {
      name: 'DRIVE_THRU',
      className: 'test_SaleType_DRIVE-THRU',
      i18nCode: '$DRIVE_LOWER'
    },
    {
      name: 'DELIVERY',
      className: 'test_SaleType_DELIVERY',
      i18nCode: '$DELIVERY'
    }
  ]
  const buttons = buttonsProps.map((buttonProps, i) => (
    isInAllSaleTypes(allSaleTypes, buttonProps.name) ?
      <ActionButton
        key={i}
        className={buttonProps.className}
        onClick={() => onSaleTypeClick(buttonProps.name)}
        disabled={orderIsInProgress && disableButton(allSaleTypes, saleType, buttonProps.name)}
        selected={selectedSaleType === buttonProps.name}
        style={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center'
        }}
      >
        <i className={buttonProps.icon} style={{ margin: '0.5vh' }}/>
        <I18N id={buttonProps.i18nCode}/>
      </ActionButton> : null
  ))
    .filter(button => button !== null)

  const saleTypeButtonsDirection = screenOrientation === ScreenOrientation.Portrait ? 'column' : 'row'
  return (
    <ButtonContainer style={{ flexDirection: saleTypeButtonsDirection }}>
      {buttons}
    </ButtonContainer>
  )
}


TotemSaleTypeRenderer.propTypes = {
  saleType: PropTypes.string,
  onSaleTypeClick: PropTypes.func,
  availableSaleTypes: PropTypes.array,
  order: PropTypes.object,
  screenOrientation: PropTypes.number
}
