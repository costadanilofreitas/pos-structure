import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'
import { FlexChild, FlexGrid, Image } from '3s-widgets'

import StaticConfigPropTypes from '../../../../prop-types/StaticConfigPropTypes'
import { BackgroundDiv, ButtonIcon, MainContainer, SaleTypeButton, SaleTypeText } from './StyledSaleTypeScreen'
import { SaleTypeBackground } from '../../../../constants/Images'


class SaleTypeScreenRenderer extends Component {
  constructor(props) {
    super(props)
    const { screenTimeout } = this.props.staticConfig

    this.timerId = null
    this.timeoutCountdown = screenTimeout
  }

  onTouch = () => {
    const { screenTimeout } = this.props.staticConfig
    this.timeoutCountdown = screenTimeout
  }

  timeoutFunction = () => {
    if (this.timeoutCountdown === 0) {
      const { toggleSaleTypeScreen } = this.props
      toggleSaleTypeScreen()
    } else if (this.timeoutCountdown > 0) {
      this.timeoutCountdown--
    }
  }

  componentDidMount() {
    window.addEventListener('touchstart', this.onTouch)
    window.addEventListener('click', this.onTouch)
    this.timerId = setInterval(this.timeoutFunction, 1000)
  }

  componentWillUnmount() {
    window.history.replaceState(null, '', '')
    window.removeEventListener('touchstart', this.onTouch, false)
    window.removeEventListener('click', this.onTouch, false)
    clearInterval(this.timerId)
  }

  render() {
    const { startKioskOrder } = this.props
    return (
      <MainContainer>
        <BackgroundDiv>
          <Image
            src={['./images/SaleTypeBackground.png', SaleTypeBackground]}
            objectFit={'cover'}
            imageWidth={'100%'}
          />
        </BackgroundDiv>
        <FlexGrid direction={'column'}>
          <FlexChild size={2}/>
          <FlexChild size={1}>
            <FlexGrid direction={'row'}>
              <FlexChild size={5} style={{ display: 'flex', justifyContent: 'flex-end' }}>
                <SaleTypeButton
                  className={'test_saleTypeScreen_EAT-IN'}
                  onClick={() => startKioskOrder('EAT_IN')}
                >
                  <ButtonIcon className={'fas fa-hamburger fa-3x'} aria-hidden="true"/>
                  <I18N id="$KIOSK_EAT_IN">
                    {(text) => (<SaleTypeText> {text} </SaleTypeText>)}
                  </I18N>
                </SaleTypeButton>
              </FlexChild>
              <FlexChild size={2}/>
              <FlexChild size={5} style={{ display: 'flex', justifyContent: 'flex-start' }}>
                <SaleTypeButton
                  className={'test_saleTypeScreen_TAKE-OUT'}
                  onClick={() => startKioskOrder('TAKE_OUT')}
                >
                  <ButtonIcon className={'fas fa-shopping-bag fa-3x'} aria-hidden="true"/>
                  <I18N id="$KIOSK_TAKE_OUT">
                    {(text) => (<SaleTypeText> {text} </SaleTypeText>)}
                  </I18N>
                </SaleTypeButton>
              </FlexChild>
            </FlexGrid>
          </FlexChild>
        </FlexGrid>
      </MainContainer>
    )
  }
}

SaleTypeScreenRenderer.propTypes = {
  staticConfig: StaticConfigPropTypes,
  startKioskOrder: PropTypes.func,
  toggleSaleTypeScreen: PropTypes.func
}

export default SaleTypeScreenRenderer

