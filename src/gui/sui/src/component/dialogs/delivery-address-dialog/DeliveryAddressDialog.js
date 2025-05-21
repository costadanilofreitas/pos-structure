import React, { Component } from 'react'
import PropTypes from 'prop-types'
import DeliveryAddressDialogRenderer from './delivery-address-renderer'
import MessageBusPropTypes from '../../../prop-types/MessageBusPropTypes'
import OrderPropTypes from '../../../prop-types/OrderPropTypes'


class DeliveryAddressDialog extends Component {
  render() {
    return <DeliveryAddressDialogRenderer{...this.props}/>
  }
}

DeliveryAddressDialog.propTypes = {
  closeDialog: PropTypes.func,
  msgBus: MessageBusPropTypes,
  order: OrderPropTypes
}

export default (DeliveryAddressDialog)
