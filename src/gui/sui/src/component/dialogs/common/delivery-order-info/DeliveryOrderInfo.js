import React, { Component } from 'react'
import injectSheet from 'react-jss'
import PropTypes from 'prop-types'
import _ from 'lodash'
import { I18N } from '3s-posui/core'
import { hasLogisticData } from '../../../../constants/LogisticStatus'
import { isDeliveryOrder } from '../../../../util/orderUtil'

import { Col, Grid, Row } from '../../../grid'
import FormItem from '../../../../app/util/form-item/JssFormItem'
import Label from '../../../label'


const styles = (theme) => ({
  container: {
    padding: theme.defaultPadding,
    height: `calc(100% - 2 * ${theme.defaultPadding})`,
    width: `calc(100% - 2 * ${theme.defaultPadding})`,
    fontSize: '2.80vmin'
  }
})

class DeliveryOrderInfo extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    const { order } = this.props
    const customProperties = {}
    _.forEach(order.CustomOrderProperties.OrderProperty, (property) => {
      customProperties[property['@attributes'].key] = property['@attributes'].value
    })

    const shortReference = 'SHORT_REFERENCE' in customProperties ? customProperties.SHORT_REFERENCE : ''
    const customerName = 'CUSTOMER_NAME' in customProperties ? customProperties.CUSTOMER_NAME : ''
    const contactNumber = 'CONTACT_NUMBER' in customProperties ? customProperties.CONTACT_NUMBER : '-'
    const change = 'CHANGE' in customProperties ? customProperties.CHANGE : ''
    const deliveryman = 'DELIVERYMAN' in customProperties ? customProperties.DELIVERYMAN : ''
    const deliverymanTime = 'DELIVERYMAN_DATETIME' in customProperties ? customProperties.DELIVERYMAN_DATETIME : ''
    const partnerCouponProduct = 'PARTNER_COUPON_PRODUCT' in customProperties ?
      customProperties.PARTNER_COUPON_PRODUCT :
      ''
    const partnerCouponDelivery = 'PARTNER_COUPON_DELIVERY' in customProperties ?
      customProperties.PARTNER_COUPON_DELIVERY :
      ''
    const merchantCouponProduct = 'MERCHANT_COUPON_PRODUCT' in customProperties ?
      customProperties.MERCHANT_COUPON_PRODUCT :
      ''
    const merchantCouponDelivery = 'MERCHANT_COUPON_DELIVERY' in customProperties ?
      customProperties.MERCHANT_COUPON_DELIVERY :
      ''

    const address = 'FORMATTED_ADDRESS' in customProperties ? customProperties.FORMATTED_ADDRESS : ''
    const deliveryFeeValue = 'DELIVERY_FEE_VALUE' in customProperties ? customProperties.DELIVERY_FEE_VALUE : ''
    const neighborhood = 'NEIGHBORHOOD' in customProperties ? customProperties.NEIGHBORHOOD : ''
    const city = 'CITY' in customProperties ? customProperties.CITY : ''
    const state = 'STATE' in customProperties ? customProperties.STATE : ''
    const formattedAddress = [address, neighborhood, city, state].join(' - ')
    const pickupType = 'PICKUP_TYPE' in customProperties ? customProperties.PICKUP_TYPE : '-'
    const observation = 'OBSERVATION' in customProperties ? customProperties.OBSERVATION : '-'
    const errorDescription = 'DELIVERY_ERROR_DESCRIPTION' in customProperties ?
      customProperties.DELIVERY_ERROR_DESCRIPTION : ''

    const isDelivery = isDeliveryOrder(customProperties)

    const adapterLogisticName = customProperties.ADAPTER_LOGISTIC_NAME?.toString().toUpperCase()
    const logisticAdapterTranslationId = `$LOGISTIC_PARTNER_${adapterLogisticName}`
    const logisticIntegrationStatus = customProperties.LOGISTIC_INTEGRATION_STATUS
    const isDefaultLogistic = adapterLogisticName === 'DEFAULT'
    const logisticData = isDefaultLogistic ? customProperties.LOGISTIC_DELIVERYMAN_DATA : customProperties.LOGISTIC_ID

    const showDeliveryPartner = isDelivery && !!adapterLogisticName && hasLogisticData(logisticIntegrationStatus)
    const showDeliverymanData = showDeliveryPartner &&
      (!isDefaultLogistic || (isDefaultLogistic && !!customProperties.LOGISTIC_DELIVERYMAN_DATA))

    return (
      <div className={styles.container}>
        <Grid fluid={true}>
          <Row>
            <Col xs={4}><FormItem label={'$SHORT_REFERENCE'} value={shortReference} position={'below'}/></Col>
            <Col xs={8}><FormItem label={'$PARTNER_CONTACT_NUMBER'} value={contactNumber} position={'below'}/></Col>
          </Row>
          <Row>
            <Col xs={12}><FormItem label={'$DLV_CUSTOMER_NAME'} value={customerName} position={'below'}/></Col>
          </Row>
          <Row>
            <Col xs={6}>
              <FormItem
                label={'$DLV_CHANGE'}
                value=<Label key="dlv_change" text={change !== '' ? change : 0} style="currency"/>
                position={'below'}
              />
            </Col>
            <Col xs={6}>
              <FormItem
                label={'$DLV_OR_PICKUP'}
                value={`$DELIVERY_${pickupType.toUpperCase()}`}
                position={'below'}
              />
            </Col>
          </Row>
          {isDelivery &&
            <Row>
              <Col xs={12}><FormItem label={'$FORMATTED_ADDRESS'} value={formattedAddress} position={'below'}/></Col>
            </Row>
          }
          {showDeliveryPartner &&
            <Row>
              <Col xs={12}>
                <FormItem label={'$DELIVERY_MAN'} value={<I18N id={logisticAdapterTranslationId} />} position={'below'}/>
              </Col>
            </Row>
          }
          {showDeliverymanData &&
            <Row>
              <Col xs={12}>
                <FormItem label={'$LOGISTIC_CODE'} value={logisticData || '-'} position={'below'}/>
              </Col>
            </Row>
          }
          { observation !== '' &&
            <Row>
              <Col xs={12}>
                <FormItem label={'$OBSERVATION'} value={observation} position={'below'}/>
              </Col>
            </Row>
          }
          { partnerCouponProduct !== '' &&
            <Row>
              <Col xs={12}>
                <FormItem
                  label={'$COUPON_DISCOUNT_IFOOD'}
                  value={<Label style={'currency'} text={partnerCouponProduct}/>}
                  position={'below'}
                />
              </Col>
            </Row>
          }
          { partnerCouponDelivery !== '' &&
            <Row>
              <Col xs={12}>
                <FormItem
                  label={'$COUPON_DISCOUNT_DELIVERY_FEE_IFOOD'}
                  value={<Label style={'currency'} text={partnerCouponDelivery}/>}
                  position={'below'}
                />
              </Col>
            </Row>
          }
          { merchantCouponProduct !== '' &&
            <Row>
              <Col xs={12}>
                <FormItem
                  label={'$COUPON_DISCOUNT_MERCHANT'}
                  value={<Label style={'currency'} text={merchantCouponProduct}/>}
                  position={'below'}
                />
              </Col>
            </Row>
          }
          { merchantCouponDelivery !== '' &&
            <Row>
              <Col xs={12}>
                <FormItem
                  label={'$COUPON_DISCOUNT_DELIVERY_FEE_MERCHANT'}
                  value={<Label style={'currency'} text={merchantCouponDelivery}/>}
                  position={'below'}
                />
              </Col>
            </Row>
          }
          { deliveryman !== '' &&
            <Row>
              <Col xs={12}>
                <FormItem label={'$DELIVERY_MAN'} value={deliveryman} position={'below'}/>
              </Col>
            </Row>
          }
          { deliverymanTime !== '' &&
            <Row>
              <Col xs={12}>
                <FormItem label={'$DELIVERY_MAN_TIME'} value={deliverymanTime} position={'below'}/>
              </Col>
            </Row>
          }
          { deliveryFeeValue !== '' &&
            <Row>
              <Col xs={12}>
                <FormItem
                  label={'$DELIVERY_FEE_VALUE'}
                  value={<Label style={'currency'} text={deliveryFeeValue}/>}
                  position={'below'}
                />
              </Col>
            </Row>
          }
          { errorDescription !== '' &&
            <Row>
              <Col xs={12}>
                <FormItem label={'$DELIVERY_ERROR'} value={errorDescription} position={'below'}/>
              </Col>
            </Row>
          }
        </Grid>
      </div>
    )
  }
}

DeliveryOrderInfo.propTypes = {
  order: PropTypes.any
}

export default injectSheet(styles)(DeliveryOrderInfo)
