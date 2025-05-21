import React, { Component } from 'react'
import PropTypes from 'prop-types'
import Img from 'react-image'
import VisibilitySensor from 'react-visibility-sensor'

import { ImageContainer, RunningIcon, DefaultBackground } from './StyledImageRenderer'


export default class ImageRenderer extends Component {
  render() {
    const { src, objectFit, containerHeight, containerWidth, background, imageHeight, imageWidth } = this.props

    return (
      <VisibilitySensor>
        <Img
          src={src}
          container={children => {
            return (
              <ImageContainer
                objectFit={objectFit}
                containerHeight={containerHeight}
                containerWidth={containerWidth}
                background={background}
                imageHeight={imageHeight}
                imageWidth={imageWidth}
              >
                {children}
              </ImageContainer>
            )
          }}
          loader={
            <RunningIcon>
              <i
                className={'fa fa-2x fa-spin fa-spinner'}
                style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}
              />
            </RunningIcon>
          }
          unloader={
            <DefaultBackground/>
          }
        />
      </VisibilitySensor>
    )
  }
}

ImageRenderer.propTypes = {
  src: PropTypes.array,
  objectFit: PropTypes.string,
  containerHeight: PropTypes.string,
  containerWidth: PropTypes.string,
  background: PropTypes.string,
  imageHeight: PropTypes.string,
  imageWidth: PropTypes.string
}
