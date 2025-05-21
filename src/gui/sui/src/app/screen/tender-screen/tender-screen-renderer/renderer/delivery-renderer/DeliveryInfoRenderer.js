import React, { Component } from 'react'
import { I18N } from '3s-posui/core'
import { FlexChild, FlexGrid } from '3s-widgets'
import OrderPropTypes from '../../../../../../prop-types/OrderPropTypes'
import MessageBusPropTypes from '../../../../../../prop-types/MessageBusPropTypes'
import { AddressContent, AddressTitle } from '../../StyledTenderScreen'
import { IconStyle } from '../../../../../../constants/commonStyles'


class DeliveryInfoRenderer extends Component {
  constructor(props) {
    super(props)

    this.state = {
      needSaleType: false
    }
  }

  customerPersonalInfoLine() {
    const { order } = this.props
    const name = order.CustomOrderProperties.CUSTOMER_NAME || ''
    const phone = order.CustomOrderProperties.CUSTOMER_PHONE || ''
    if (name || phone) {
      return (
        <AddressContent>
          {`${name} ${phone}`}
        </AddressContent>
      )
    }
    return null
  }

  customerAddressLine() {
    const { order } = this.props
    const street = order.CustomOrderProperties.STREET_NAME || ''
    const streetNumber = order.CustomOrderProperties.STREET_NUMBER || ''
    const complement = order.CustomOrderProperties.COMPLEMENT || ''
    if (street || streetNumber || complement) {
      return (
        <AddressContent>
          { streetNumber ? `${street} ${streetNumber}, ${complement}` : `${street} ${complement}`}
        </AddressContent>
      )
    }
    return null
  }

  customerAddressLine2() {
    const { order } = this.props
    const zipCode = order.CustomOrderProperties.POSTAL_CODE || ''
    const neighborhood = order.CustomOrderProperties.NEIGHBORHOOD || ''
    if (neighborhood || zipCode) {
      return (
        <AddressContent>
          {zipCode &&
          <I18N id={'$ZIP_CODE'}/>
          }
          { zipCode ? ` - ${zipCode} - ${neighborhood}` : `${neighborhood}`}
        </AddressContent>
      )
    }
    return null
  }

  customerReferenceLine() {
    const { order } = this.props
    const reference = order.CustomOrderProperties.ADDRESS_REFERENCE || ''
    if (reference) {
      return (
        <AddressContent>
          {`${reference}`}
        </AddressContent>
      )
    }
    return null
  }

  render() {
    const { msgBus } = this.props

    return (
      <FlexGrid direction={'column'}>
        <FlexChild size={3}/>
        <FlexChild size={2}>
          <FlexGrid direction={'row'}>
            <FlexChild size={6}>
              <AddressTitle>
                <I18N id={'$DELIVERY_INFO'}/>
              </AddressTitle>
              {this.customerPersonalInfoLine()}
              {this.customerAddressLine()}
              {this.customerAddressLine2()}
              {this.customerReferenceLine()}
            </FlexChild>
            <FlexChild size={1}>
              <IconStyle
                style={{ fontSize: '4vmin' }}
                className={'fas fa-edit fa-3x'}
                onClick={() => msgBus.syncAction('delivery_address')}
              />
            </FlexChild>
          </FlexGrid>
        </FlexChild>
      </FlexGrid>
    )
  }
}

DeliveryInfoRenderer.propTypes = {
  order: OrderPropTypes,
  msgBus: MessageBusPropTypes
}

export default DeliveryInfoRenderer
