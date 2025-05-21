import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { FlexChild } from '3s-widgets'
import { TextBoxContainer } from './StyledCommonRenderer'


export default class TextRenderer extends Component {
  render() {
    const { text, showText, textContainerSize, textContainerStyle, fontColor } = this.props

    if (!showText || text == null) {
      return null
    }

    return (
      <FlexChild size={textContainerSize} style={{ height: '100%' }}>
        <TextBoxContainer style={textContainerStyle} fontColor={fontColor}>
          {text}
        </TextBoxContainer>
      </FlexChild>
    )
  }
}

TextRenderer.propTypes = {
  fontColor: PropTypes.string,
  showText: PropTypes.bool,
  text: PropTypes.string,
  textContainerSize: PropTypes.number,
  textContainerStyle: PropTypes.object
}
