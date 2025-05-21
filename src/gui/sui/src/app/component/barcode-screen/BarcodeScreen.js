import React, { PureComponent } from 'react'

import BarcodeScreenRenderer from './barcode-screen-renderer'


class BarcodeScreen extends PureComponent {
  constructor(props) {
    super(props)
  }

  render() {
    return <BarcodeScreenRenderer {...this.props}/>
  }
}

export default BarcodeScreen
