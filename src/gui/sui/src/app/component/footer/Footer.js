import React, { Component } from 'react'

import FooterRenderer from './footer-renderer'
import OrderPropTypes from '../../../prop-types/OrderPropTypes'
import MessageBusPropTypes from '../../../prop-types/MessageBusPropTypes'


export default class Footer extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    return <FooterRenderer {...this.props}/>
  }
}

Footer.propTypes = {
  order: OrderPropTypes,
  msgBus: MessageBusPropTypes
}
