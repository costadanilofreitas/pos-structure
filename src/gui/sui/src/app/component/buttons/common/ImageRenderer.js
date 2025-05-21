import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { FlexChild, Image } from '3s-widgets'
import { FaIconContainer } from './StyledCommonRenderer'


export default class ImageRenderer extends Component {
  render() {
    const { showImage, imageContainerSize, imageName, imageContainerStyle, faIcon } = this.props

    if (!showImage || (imageName == null && faIcon == null)) {
      return null
    }

    if (faIcon != null) {
      return (
        <FlexChild size={imageContainerSize}>
          <FaIconContainer>
            <i className={faIcon} aria-hidden="true"/>
          </FaIconContainer>
        </FlexChild>
      )
    }

    return (
      <FlexChild size={imageContainerSize} style={imageContainerStyle}>
        <Image
          src={[`./images/${imageName}.png`]}
          width={'98%'}
        />
      </FlexChild>
    )
  }
}

ImageRenderer.propTypes = {
  showImage: PropTypes.bool,
  imageName: PropTypes.string,
  faIcon: PropTypes.string,
  imageContainerSize: PropTypes.number,
  imageContainerStyle: PropTypes.object
}
