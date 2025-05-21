import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { Image } from '3s-widgets'

import { FooterImage } from '../../../../constants/Images'


class TotemFooterRenderer extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    return (
      <div onDoubleClick={()=> window.location.reload(true)} className={this.props.classes.totemFooter}>
        <Image src={['./images/FooterImage.png', FooterImage]}/>
      </div>
    )
  }
}

TotemFooterRenderer.propTypes = {
  classes: PropTypes.object
}

export default TotemFooterRenderer
