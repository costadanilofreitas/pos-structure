import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { FlexChild, FlexGrid, Image } from '3s-widgets'
import { I18N } from '3s-posui/core'

import StaticConfigPropTypes from '../../../../prop-types/StaticConfigPropTypes'
import { Background, BottomText, Color, ReadyColor, ReadyText } from './StyledConfirmationScreenRenderer'
import { LogoImageConfirmationScreen, TotemImageConfirmationScreen } from '../../../../constants/Images'

class ConfirmationScreenRenderer extends Component {
  constructor(props) {
    super(props)

    this.timerId = null
    this.time = this.props.staticConfig.totemConfigurations.confirmationScreen.timeout
    this.timeoutFunction = this.timeoutFunction.bind(this)
  }

  timeoutFunction = () => {
    if (this.time === 0) {
      const { cancelConfirmationScreen } = this.props
      cancelConfirmationScreen()
    }
    if (this.time > 0) {
      this.time--
    }
  }

  render() {
    return (
      <Background>
        <FlexGrid direction={'column'} className={'test_ConfirmationScreenRenderer_SCREEN'}>
          <FlexChild size={1}>
            <Image
              src={['./images/LogoImageConfirmation.png', LogoImageConfirmationScreen]}
              objectFit={'scale-down'}
              background={'transparent'}
            />
          </FlexChild>
          <FlexChild size={2}>
            <ReadyText>
              <ReadyColor>
                <I18N id="$FINISHED" defaultMessage="CLICK TO START"/>
              </ReadyColor>
              <br/>
              <I18N id="$END_PAYMENT_TEXT_1" defaultMessage="CLICK TO START"/>
              <Color>
                <I18N id="$END_PAYMENT_TEXT_2" defaultMessage="CLICK TO START"/>
              </Color>
              <I18N id="$END_PAYMENT_TEXT_3" defaultMessage="CLICK TO START"/>
            </ReadyText>
          </FlexChild>
          <FlexChild size={3}>
            <Image
              src={['./images/TotemImageConfirmation.png', TotemImageConfirmationScreen]}
              background={'transparent'}
            />
          </FlexChild>
          <FlexChild size={1}>
            <BottomText>
              <Color>
                <I18N id="$THANK_TEXT" defaultMessage="CLICK TO START"/>
              </Color>
            </BottomText>
          </FlexChild>
        </FlexGrid>
      </Background>
    )
  }

  componentDidMount() {
    this.timerId = setInterval(this.timeoutFunction, 1000)
  }
}

ConfirmationScreenRenderer.propTypes = {
  staticConfig: StaticConfigPropTypes,
  cancelConfirmationScreen: PropTypes.func
}

export default ConfirmationScreenRenderer
