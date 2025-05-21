import React, { Component } from 'react'
import PropTypes from 'prop-types'

import ImageRenderer from './renderer'


export default class Image extends Component {

  render() {
    const { src, objectFit, containerHeight, containerWidth, background, imageHeight, imageWidth } = this.props

    return (
      <ImageRenderer
        src={src}
        objectFit={objectFit}
        containerHeight={containerHeight}
        containerWidth={containerWidth}
        background={background}
        imageHeight={imageHeight}
        imageWidth={imageWidth}
      />
    )
  }
}

Image.propTypes = {
  src: PropTypes.array,
  objectFit: PropTypes.string,
  containerHeight: PropTypes.string,
  containerWidth: PropTypes.string,
  background: PropTypes.string,
  imageHeight: PropTypes.string,
  imageWidth: PropTypes.string
}

Image.defaultProps = {
  src: [],
  objectFit: 'contain',
  containerHeight: '100%',
  containerWidth: '100%',
  imageHeight: '100%',
  imageWidth: 'auto'
}
