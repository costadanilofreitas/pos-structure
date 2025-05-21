import React from 'react'
import PropTypes from 'prop-types'

import RendererChooser from '../../../../component/renderer-chooser'
import { DesktopRenderer, MobileRenderer, TotemRenderer } from './JssTableDetailsRenderer'
import TableType from '../../../model/TableType'


export default function TableDetailsRenderer({ tableInfo, showMobile, compact }) {
  const rendererTableDetails = []
  tableInfo.details.forEach(detail => {
    const rendererDetail = {
      id: detail.id,
      value: detail.value,
      compact: detail.compact,
      labelStyle: '',
      icon: ''
    }
    switch (detail.id) {
      case 'status':
        rendererDetail.label = '$STATUS'
        rendererDetail.icon = 'fas fa-info-circle'
        break
      case 'sector':
        rendererDetail.label = '$SECTOR'
        rendererDetail.icon = 'fas fa-map-marker-alt'
        break
      case 'operator':
        rendererDetail.label = '$OPERATOR'
        rendererDetail.icon = 'fas fa-user-tie'
        break
      case 'numberOfOrders':
        rendererDetail.label = '$TOTAL_ORDERS'
        rendererDetail.icon = 'fas fa-edit'
        break
      case 'tableAmount':
        rendererDetail.label = '$TOTAL_AMOUNT'
        rendererDetail.icon = 'fas fa-coins'
        rendererDetail.labelStyle = 'currency'
        break
      case 'numberOfSeats':
        rendererDetail.label = '$SEATS'
        rendererDetail.icon = 'fas fa-users'
        break
      case 'averageTicket':
        rendererDetail.label = '$AVERAGE_TICKET'
        rendererDetail.icon = 'fas fa-dollar-sign'
        rendererDetail.labelStyle = 'currency'
        break
      case 'timeOpened':
        rendererDetail.label = '$TIME_OPENED'
        rendererDetail.icon = 'fas fa-user-clock'
        rendererDetail.labelStyle = rendererDetail.value === '-' ? '' : 'datetimeMillisecondsSpan'
        break
      case 'lastUpdateTime':
        rendererDetail.label = '$LAST_SERVICE'
        rendererDetail.icon = 'fas fa-concierge-bell'
        rendererDetail.labelStyle = rendererDetail.value === '-' ? '' : 'datetimeMillisecondsSpan'
        break
      case 'linkedTables':
        rendererDetail.label = '$LINKED_TABLES'
        rendererDetail.icon = 'fas fa-link'
        rendererDetail.value = rendererDetail.value.join(', ')
        break
      case 'specialCatalog':
        rendererDetail.label = '$SPECIAL_CATALOG_TABLE'
        rendererDetail.icon = 'fas fa-birthday-cake'
        break
      default:
        break
    }
    rendererTableDetails.push(rendererDetail)
  })

  const tabText = tableInfo.number ? `$TAB_INFORMATION|${tableInfo.number}` : '$NEW_TAB'
  const titleId = (tableInfo.type === TableType.Seat ? `$TABLE_INFORMATION|${tableInfo.number}` : tabText)

  const info = {
    title: titleId,
    details: rendererTableDetails
  }

  if (showMobile === true) {
    return <MobileRenderer tableInfo={info}/>
  }

  return (
    <RendererChooser
      mobile={<MobileRenderer tableInfo={info}/>}
      desktop={<DesktopRenderer tableInfo={info} compact={compact}/>}
      totem={<TotemRenderer tableInfo={info} compact={compact}/>}
    />
  )
}

TableDetailsRenderer.propTypes = {
  tableInfo: PropTypes.shape({
    type: PropTypes.number,
    number: PropTypes.string,
    details: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.string,
      value: PropTypes.any
    }))
  }),
  showMobile: PropTypes.bool,
  compact: PropTypes.bool
}
