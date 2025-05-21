import React from 'react'
import PropTypes from 'prop-types'
import includes from 'lodash/includes'
import flatten from 'lodash/flatten'
import _find from 'lodash/find'

import { I18N } from '3s-posui/core'
import { FlexChild, FlexGrid } from '3s-widgets'

import ActionButton from '../../../../component/action-button'
import DeviceType from '../../../../constants/Devices'


function isInAllSaleTypes(allSaleTypes, saleType) {
  return includes(flatten(allSaleTypes), saleType)
}

function disableButton(allSaleTypes, saleType, buttonSaleType) {
  const allowedSaleTypes = _find(allSaleTypes, (types) => includes(types, saleType))
  return !includes(allowedSaleTypes, buttonSaleType)
}

export default function SaleTypeRenderer({
  saleType, onSaleTypeClick, classes, availableSaleTypes, order, deviceType
}) {
  const allSaleTypes = _.isEmpty(availableSaleTypes) ? [['EAT_IN']] : availableSaleTypes

  const firstAvailableSaleType = allSaleTypes[0][0]
  const selectedSaleType = isInAllSaleTypes(allSaleTypes, saleType) ? saleType : firstAvailableSaleType
  const orderIsInProgress = order.state === 'IN_PROGRESS'

  return (
    <div className={classes.container}>
      <FlexGrid direction={'row'}>
        {isInAllSaleTypes(allSaleTypes, 'EAT_IN') &&
        <FlexChild>
          <ActionButton
            style={{ fontSize: '2vmin' }}
            className={['test_SaleType_EAT-IN', selectedSaleType === 'EAT_IN' ? classes.selected : ''].join(' ')}
            onClick={() => onSaleTypeClick('EAT_IN')}
            disabled={orderIsInProgress && disableButton(allSaleTypes, saleType, 'EAT_IN')}
            selected={selectedSaleType === 'EAT_IN'}
          >
            {<I18N id={'$EAT_IN'}/>}
          </ActionButton>
        </FlexChild>}
        {isInAllSaleTypes(allSaleTypes, 'TAKE_OUT') &&
        <FlexChild>
          <ActionButton
            style={{ fontSize: '2vmin' }}
            className={['test_SaleType_TAKE-OUT', selectedSaleType === 'TAKE_OUT' ? classes.selected : ''].join(' ')}
            onClick={() => onSaleTypeClick('TAKE_OUT')}
            disabled={orderIsInProgress && disableButton(allSaleTypes, saleType, 'TAKE_OUT')}
            selected={selectedSaleType === 'TAKE_OUT'}
          >
            {<I18N id={'$TAKE_OUT'}/>}
          </ActionButton>
        </FlexChild>}
        {isInAllSaleTypes(allSaleTypes, 'DRIVE_THRU') &&
        <FlexChild>
          <ActionButton
            style={{ fontSize: '2vmin' }}
            className={['test_SaleType_DRIVE-THRU', selectedSaleType === 'DRIVE_THRU' ? classes.selected : ''].join(' ')}
            onClick={() => onSaleTypeClick('DRIVE_THRU')}
            disabled={orderIsInProgress && disableButton(allSaleTypes, saleType, 'DRIVE_THRU')}
            selected={selectedSaleType === 'DRIVE_THRU'}
          >
            {<I18N id={'$DRIVE_LOWER'}/>}
          </ActionButton>
        </FlexChild>}
        {isInAllSaleTypes(allSaleTypes, 'DELIVERY') && deviceType !== DeviceType.Mobile &&
        <FlexChild>
          <ActionButton
            style={{ fontSize: '2vmin' }}
            className={['test_SaleType_DELIVERY', selectedSaleType === 'DELIVERY' ? classes.selected : ''].join(' ')}
            onClick={() => onSaleTypeClick('DELIVERY')}
            disabled={orderIsInProgress && disableButton(allSaleTypes, saleType, 'DELIVERY')}
            selected={selectedSaleType === 'DELIVERY'}
          >
            {<I18N id={'$DELIVERY'}/>}
          </ActionButton>
        </FlexChild>}
      </FlexGrid>
    </div>
  )
}


SaleTypeRenderer.propTypes = {
  saleType: PropTypes.string,
  onSaleTypeClick: PropTypes.func,
  classes: PropTypes.object,
  availableSaleTypes: PropTypes.array,
  order: PropTypes.object,
  deviceType: PropTypes.number
}
