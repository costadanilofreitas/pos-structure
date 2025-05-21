import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { FlexChild, FlexGrid, Image } from '3s-widgets'
import { I18N } from '3s-posui/core'

import MessageBusPropTypes from '../../../../prop-types/MessageBusPropTypes'
import StaticConfigPropTypes from '../../../../prop-types/StaticConfigPropTypes'
import SaleTypeScreen from '../../sale-type-screen'
import { BackgroundDiv, ClickImage, ClickImageX, ClickImageY, ClickText, MainContainer } from './StyledWelcomeScreen'
import { ImageBackgroundWelcomeScreen, PopupImageWelcomeScreen, VideoBackgroundWelcomeScreen } from '../../../../constants/Images'
import { getJoinedAvailableSaleTypes } from '../../../util/saleTypeConverter'

class WelcomeScreenRenderer extends Component {
  constructor(props) {
    super(props)

    this.state = {
      needSaleType: false
    }
  }

  toggleSaleTypeScreen = () => {
    const { needSaleType } = this.state
    this.setState({ needSaleType: !needSaleType })
  }

  startKioskOrder = (saleType) => {
    const { msgBus } = this.props
    msgBus.syncAction('do_start_kiosk_order', saleType)
  }

  checkAvailableSaleTypes = (availableSaleTypes) => {
    const saleTypesList = getJoinedAvailableSaleTypes(availableSaleTypes)

    if (saleTypesList.length === 1) {
      this.startKioskOrder(saleTypesList[0])
    } else {
      this.toggleSaleTypeScreen()
    }
  }

  getTouchPopup(classes, showPopup) {
    if (showPopup) {
      return (
        <ClickImageX>
          <ClickImageY>
            <FlexGrid direction={'column'}>
              <FlexChild>
                <ClickImage>
                  <Image
                    src={[PopupImageWelcomeScreen]}
                    containerHeight={'80%'}
                    containerWidth={'80%'}
                    imageWidth={'80%'}
                    imageHeight={'80%'}
                    background={'transparent'}
                  />
                </ClickImage>
              </FlexChild>
              <FlexChild>
                <ClickText>
                  <I18N id="$CLICK_TO_START" defaultMessage="CLICK TO START"/>
                </ClickText>
              </FlexChild>
            </FlexGrid>
          </ClickImageY>
        </ClickImageX>
      )
    }

    return null
  }

  getBackground(classes, format) {
    if (format.toLowerCase() === 'image') {
      return (
        <BackgroundDiv>
          <Image
            src={['./images/WelcomeScreenBackground.png', ImageBackgroundWelcomeScreen]}
            objectFit={'cover'}
            imageWidth={'100%'}
          />
        </BackgroundDiv>
      )
    }
    return (
      <video loop autoPlay muted src={VideoBackgroundWelcomeScreen} className={classes.background}/>
    )
  }

  renderSaleType() {
    return (
      <SaleTypeScreen
        startKioskOrder={this.startKioskOrder}
        toggleSaleTypeScreen={this.toggleSaleTypeScreen}
      />
    )
  }

  renderWelcomeScreen() {
    const { classes, staticConfig } = this.props
    const backgroundFormat = staticConfig.totemConfigurations.welcomeScreen.backgroundFormat
    const isShowPopup = staticConfig.totemConfigurations.welcomeScreen.showPopup
    const availableSaleTypes = staticConfig.availableSaleTypes

    return (
      <MainContainer
        className={'test_WelcomeScreen_CONTAINER'}
        onClick={() => this.checkAvailableSaleTypes(availableSaleTypes)}
      >
        {this.getBackground(classes, backgroundFormat)}
        {this.getTouchPopup(classes, isShowPopup)}
      </MainContainer>
    )
  }

  render() {
    const { needSaleType } = this.state
    return (needSaleType ? this.renderSaleType() : this.renderWelcomeScreen())
  }
}

WelcomeScreenRenderer.propTypes = {
  classes: PropTypes.object,
  msgBus: MessageBusPropTypes,
  staticConfig: StaticConfigPropTypes
}

export default WelcomeScreenRenderer
