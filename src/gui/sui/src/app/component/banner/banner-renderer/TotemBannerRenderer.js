import React, { Component } from 'react'
import { Fade } from 'react-slideshow-image'
import PropTypes from 'prop-types'

import { Image } from '3s-widgets'

import StaticConfigPropTypes from '../../../../prop-types/StaticConfigPropTypes'
import MessageBusPropTypes from '../../../../prop-types/MessageBusPropTypes'
import OrderPropTypes from '../../../../prop-types/OrderPropTypes'
import { ContainerSlide, MainContainer } from './StyledBannerRenderer'
import OrderState from '../../../model/OrderState'
import { orderHasAttribute, orderInState } from '../../../util/orderValidator'
import { DefaultBanner1, DefaultBanner2 } from '../../../../constants/Images'

class TotemBannerRenderer extends Component {
  constructor(props) {
    super(props)
    this.slideRef = React.createRef()

    this.doSaleBanner = this.doSaleBanner.bind(this)
  }

  doSaleBanner(index) {
    const { msgBus, order, saleType } = this.props
    const orderId = this.bannerConfigImages[index].productId || ''
    if (orderHasAttribute(order, 'state') && orderInState(order, OrderState.InProgress) && orderId !== '') {
      msgBus.syncAction('doCompleteOption',
        '1',
        orderId,
        '1',
        '',
        '',
        saleType)
    }
  }

  insertImage(imagePath, index) {
    return (
      <Image
        key={index}
        src={imagePath}
        imageWidth={'100%'}
        objectFit={'cover'}
      />
    )
  }

  render() {
    const { visible, bannerConfig } = this.props

    const bannerImages = bannerConfig.images.map((imageData, i) => {
      return this.insertImage([imageData.path, i % 2 === 0 ? DefaultBanner1 : DefaultBanner2], i)
    })

    this.bannerConfigImages = bannerImages.length > 0 ? bannerConfig.images : [{}, {}]

    this.bannerImages = []

    if (bannerImages.length > 0) {
      this.bannerImages = bannerImages
    } else {
      this.bannerImages.push(
        this.insertImage([DefaultBanner1], 0),
        this.insertImage([DefaultBanner2], 1)
      )
    }

    if (!visible) {
      return null
    }

    const properties = {
      duration: 5000,
      transitionDuration: 500,
      infinite: true,
      autoplay: true,
      arrows: false,
      indicators: false
    }

    return (
      <MainContainer onClick={() => this.doSaleBanner(this.slideRef.current.state.index)}>
        <ContainerSlide>
          {
            this.bannerImages.length > 1 ?
              <Fade {...properties} ref={this.slideRef}>
                {this.bannerImages}
              </Fade> :
              <div onClick={() => this.doSaleBanner(0)}>
                {this.bannerImages}
              </div>
          }
        </ContainerSlide>
      </MainContainer>
    )
  }
}

TotemBannerRenderer.propTypes = {
  staticConfig: StaticConfigPropTypes,
  bannerConfig: PropTypes.shape({
    images: PropTypes.arrayOf(PropTypes.shape({ path: PropTypes.string, productId: PropTypes.string }))
  }),
  msgBus: MessageBusPropTypes,
  order: OrderPropTypes,
  saleType: PropTypes.string,
  visible: PropTypes.bool
}

TotemBannerRenderer.defaultProps = {
  visible: true
}

export default TotemBannerRenderer
