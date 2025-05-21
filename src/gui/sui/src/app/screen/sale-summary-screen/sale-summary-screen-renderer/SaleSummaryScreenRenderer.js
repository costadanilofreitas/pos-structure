import React, { Component } from 'react'

import { FlexChild, FlexGrid, Image } from '3s-widgets'
import { I18N } from '3s-posui/core'


import {
  BackgroundDiv,
  ButtonContainer,
  ButtonIcon,
  MainContainer,
  SalePanelDiv,
  SummaryButton,
  SummaryButtonText,
  SummaryTitle,
  SalePanelContainer
} from './StyledSaleSummaryScreen'
import { ImageBackgroundOrderScreen } from '../../../../constants/Images'
import OrderPropTypes from '../../../../prop-types/OrderPropTypes'
import CustomSalePanel from '../../../component/custom-sale-panel'
import TenderScreen from '../../tender-screen'


class SaleSummaryScreenRenderer extends Component {
  constructor(props) {
    super(props)

    this.state = {
      tenderScreen: false
    }
  }

  getCustomSalePanel() {
    const { order }
      = this.props
    return (
      <SalePanelDiv>
        <CustomSalePanel
          order={order}
          showSummary={true}
          showHeader={false}
          showSummaryPayment={false}
          showSummarySubtotal={false}
          showSummaryTotal={true}
          styleOverflow={true}
          saleSummaryStyle={'totemSaleSummaryLineRoot'}
          salePanelBackground={false}
          showSeatInSalePanelLine={false}
          biggerFont={true}
        />
      </SalePanelDiv>
    )
  }

  toggleTenderScreen = () => {
    const { tenderScreen } = this.state
    this.setState({ tenderScreen: !tenderScreen })
  }

  renderTenderScreen() {
    return (
      <TenderScreen
        toggleTenderScreen={this.toggleTenderScreen}
      />
    )
  }

  renderSummaryScreen() {
    return (
      <MainContainer>
        <BackgroundDiv>
          <Image
            src={['./images/OrderScreenBackground.png', ImageBackgroundOrderScreen]}
            objectFit={'cover'}
            imageWidth={'100%'}
          />
        </BackgroundDiv>
        <FlexGrid direction={'column'}>
          <FlexChild size={0.6}>
            <SummaryTitle>
              <I18N id="$ORDER_SUMMARY"/>
            </SummaryTitle>
          </FlexChild>
          <FlexChild size={2}>
            <SalePanelContainer>
              {this.getCustomSalePanel()}
            </SalePanelContainer>
          </FlexChild>
          <FlexChild size={1}>
            <FlexGrid direction={'row'}>
              <FlexChild size={5}>
                <ButtonContainer flexPosition={'flex-end'}>
                  <SummaryButton
                    className={'test_SaleSummaryScreen_BACK'}
                    executeAction={() => ['do_back_from_total']}
                  >
                    <ButtonIcon className={'fas fa-arrow-circle-left fa-2x'} aria-hidden="true"/>
                    <I18N id="$PREVIOUS">
                      {(text) => (<SummaryButtonText> {text} </SummaryButtonText>)}
                    </I18N>
                  </SummaryButton>
                </ButtonContainer>
              </FlexChild>
              <FlexChild size={2}/>
              <FlexChild size={5}>
                <ButtonContainer flexPosition={'flex-start'}>
                  <SummaryButton
                    className={'test_SaleSummaryScreen_NEXT'}
                    onClick={this.toggleTenderScreen}
                  >
                    <ButtonIcon className={'fas fa-arrow-circle-right fa-2x'} aria-hidden="true"/>
                    <I18N id="$NEXT">
                      {(text) => (<SummaryButtonText> {text} </SummaryButtonText>)}
                    </I18N>
                  </SummaryButton>
                </ButtonContainer>
              </FlexChild>
            </FlexGrid>
          </FlexChild>
        </FlexGrid>
      </MainContainer>
    )
  }

  render() {
    const { tenderScreen } = this.state
    return (tenderScreen ? this.renderTenderScreen() : this.renderSummaryScreen())
  }
}

SaleSummaryScreenRenderer.propTypes = {
  order: OrderPropTypes
}

export default SaleSummaryScreenRenderer
