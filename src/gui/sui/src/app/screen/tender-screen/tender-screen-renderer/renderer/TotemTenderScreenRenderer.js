import React from 'react'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'
import { FlexChild, FlexGrid, Image } from '3s-widgets'

import themes from '../../../../../constants/themes'
import { findChildByType } from '../../../../../util/renderUtil'
import OrderTenders from '../../../../component/order-tenders'
import OrderTotal from '../../../../component/order-total'
import {
  BackgroundDiv,
  CustomerButton,
  CustomerInfoContainer,
  CustomerInfoTable,
  CustomerName,
  FlexChildAligner,
  MainContainer,
  MainTitle,
  ReturnContainer,
  ReturnDiv,
  ReturnText
} from '../StyledTenderScreen'
import MessageBusPropTypes from '../../../../../prop-types/MessageBusPropTypes'
import OrderPropTypes from '../../../../../prop-types/OrderPropTypes'
import { LogoImageTenderScreen, ImageBackgroundTenderScreen } from '../../../../../constants/Images'

function TotemTenderScreenRenderer(props) {
  const { children, order, customOrder, toggleTenderScreen, msgBus } = props
  let customerDoc = ((customOrder || order).CustomOrderProperties || {}).CUSTOMER_DOC
  let customerName = ((customOrder || order).CustomOrderProperties || {}).CUSTOMER_NAME
  customerDoc = customerDoc === 'None' ? null : customerDoc
  customerName = customerName === 'None' ? null : customerName

  function renderCustomerInfo() {
    return (
      <CustomerInfoContainer>
        <p style={{ fontWeight: 'bold' }}>
          <I18N id={'$CUSTOMER_INFO'}/>
        </p>
        <CustomerInfoTable>
          <FlexGrid direction={'column'}>
            <FlexChild>
              <FlexGrid>
                <FlexChildAligner>
                  <I18N id={'$NAME'}/>:
                </FlexChildAligner>
                <FlexChildAligner size={3}>
                  <CustomerName>
                    {customerName != null ? customerName : <I18N id={'$NOT_INFORMED'}/>}
                  </CustomerName>
                </FlexChildAligner>
                <FlexChildAligner>
                  <CustomerButton
                    className={'test_TenderScreenRenderer_CHANGE-NAME'}
                    onClick={() => msgBus.syncAction('doSetCustomerName')}
                  >
                    <i className={'fas fa-user-edit'} aria-hidden="true"/>
                  </CustomerButton>
                </FlexChildAligner>
              </FlexGrid>
            </FlexChild>
            <FlexChild>
              <FlexGrid>
                <FlexChildAligner>
                  <I18N id={'$SALE_CUSTOMER_DOC'}/>:
                </FlexChildAligner>
                <FlexChildAligner size={3}>
                  {customerDoc != null ? customerDoc : <I18N id={'$NOT_INFORMED'}/>}
                </FlexChildAligner>
                <FlexChildAligner>
                  <CustomerButton
                    className={'test_TenderScreenRenderer_CHANGE-DOCUMENT'}
                    onClick={() => msgBus.syncAction('doSetCustomerDocument')}
                  >
                    <i className={'far fa-id-card'} aria-hidden="true"/>
                  </CustomerButton>
                </FlexChildAligner>
              </FlexGrid>
            </FlexChild>
          </FlexGrid>
        </CustomerInfoTable>
      </CustomerInfoContainer>
    )
  }

  return (
    <MainContainer>
      <BackgroundDiv>
        <Image
          src={['./images/TenderScreenBackground.png', ImageBackgroundTenderScreen]}
          objectFit={'cover'}
          imageWidth={'100%'}
        />
      </BackgroundDiv>
      <FlexGrid direction={'column'}>
        <FlexChild size={2}>
          <Image
            src={['./images/ImgLogo.png', LogoImageTenderScreen]}
            objectFit={'scale-down'}
            background={'transparent'}
          />
        </FlexChild>
        <FlexChild size={2}>
          {renderCustomerInfo()}
        </FlexChild>
        <FlexChild size={1}>
          {findChildByType(children, OrderTotal)}
        </FlexChild>
        <FlexChild size={4}>
          <MainTitle>
            <I18N id={'$SELECT_PAYMENT_METHOD'}/>
          </MainTitle>
          {findChildByType(children, OrderTenders)}
        </FlexChild>
        <FlexChild size={0.5}>
          <ReturnContainer>
            <ReturnDiv
              theme={themes[0]}
              onClick={toggleTenderScreen}
              className={'test_TenderScreenRenderer_BACK'}
            >
              <I18N id="$BACK">
                {(text) => (<ReturnText> {text} </ReturnText>)}
              </I18N>
            </ReturnDiv>
          </ReturnContainer>
        </FlexChild>
      </FlexGrid>
    </MainContainer>
  )
}


TotemTenderScreenRenderer.propTypes = {
  children: PropTypes.oneOfType([PropTypes.array, PropTypes.object]),
  msgBus: MessageBusPropTypes,
  order: OrderPropTypes,
  customOrder: OrderPropTypes,
  toggleTenderScreen: PropTypes.func
}

export default TotemTenderScreenRenderer
