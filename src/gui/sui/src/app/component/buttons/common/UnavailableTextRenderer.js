import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { FlexChild } from '3s-widgets'
import { I18N } from '3s-posui/core'

import { TextBoxContainer } from './StyledCommonRenderer'


export default class UnavailableTextRenderer extends Component {
  render() {
    const { enabled, unavailableTextSize } = this.props

    if (!enabled) {
      return null
    }

    return (
      <FlexChild size={unavailableTextSize} style={{ height: '100%' }}>
        <TextBoxContainer>
          <I18N id="$UNAVAILABLE"/>
        </TextBoxContainer>
      </FlexChild>
    )
  }
}

UnavailableTextRenderer.propTypes = {
  enabled: PropTypes.bool,
  unavailableTextSize: PropTypes.number
}

UnavailableTextRenderer.defaultProps = {
  enabled: false
}
