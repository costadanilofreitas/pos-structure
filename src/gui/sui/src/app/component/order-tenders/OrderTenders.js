import React, { Component } from 'react'

import OrderTendersRenderer from './order-tenders-renderer'


export default class OrderTenders extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    return <OrderTendersRenderer {...this.props} />
  }
}

