import React, { Component } from 'react'
import PropTypes from 'prop-types'

import RendererChooser from '../../../../../component/renderer-chooser'
import DefaultRenderer from './renderers/DefaultRenderer'
import TotemRenderer from './renderers/TotemRenderer'


class SalePanelItemOptions extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    return (<RendererChooser
      desktop={<DefaultRenderer {...this.props}/>}
      mobile={<DefaultRenderer {...this.props}/>}
      totem={<TotemRenderer {...this.props}/>}
    />)
  }
}

SalePanelItemOptions.propTypes = {
  classes: PropTypes.object,
  itemQuantity: PropTypes.number,
  lineNumber: PropTypes.number,
  changeQuantity: PropTypes.func,
  deleteLines: PropTypes.func,
  showModifierScreen: PropTypes.func,
  onDelete: PropTypes.func
}

export default SalePanelItemOptions
