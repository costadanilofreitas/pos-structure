import React from 'react'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'
import { IconStyle, CommonStyledButton } from '../../../../../constants/commonStyles'
import ButtonGrid from '../../../button-grid/ButtonGrid'


export const TotaledOrderRenderer = (props) => {
  const { isCashier } = props

  return (
    <ButtonGrid
      direction="column"
      cols={2}
      rows={2}
      buttons={{
        0:
            <CommonStyledButton
              className={'test_OrderActionsRenderer_BACK-TO-ORDER'}
              executeAction={() => ['do_back_from_total']}
              border={true}
              disabled={isCashier}
            >
              <IconStyle
                className="fas fa-arrow-circle-left fa-2x"
                disabled={isCashier}
              />
              <br/>
              <I18N id="$BACK_TO_ORDER"/>
            </CommonStyledButton>,
        1:
            <CommonStyledButton
              className={'test_OrderActionsRenderer_SAVE-ORDER'}
              executeAction={['doStoreOrder']}
              border={true}
            >
              <IconStyle className="far fa-save fa-2x"/>
              <br/>
              <I18N id="$SAVE_ORDER"/>
            </CommonStyledButton>,
        2:
            <CommonStyledButton
              className={'test_OrderActionsRenderer_COSTUMER-NAME'}
              executeAction={() => ['doSetCustomerName']}
              border={true}
            >
              <IconStyle className="fas fa-user-edit fa-2x"/>
              <br/>
              <I18N id="$CUSTOMER_NAME"/>
            </CommonStyledButton>,
        3:
            <CommonStyledButton
              className={'test_OrderActionsRenderer_COSTUMER-DOC'}
              executeAction={() => ['doSetCustomerDocument']}
              border={true}
            >
              <IconStyle className="far fa-id-card fa-2x"/>
              <br/>
              <I18N id="$CUSTOMER_DOC"/>
            </CommonStyledButton>
      }}
    />
  )
}

TotaledOrderRenderer.propTypes = {
  isCashier: PropTypes.bool
}

export function checkOrderItems(order) {
  let orderHasItems = false
  if (Array.isArray(order.SaleLine)) {
    for (let i = 0; i < order.SaleLine.length; i++) {
      if (parseInt(order.SaleLine[i].level, 10) === 0 && parseInt(order.SaleLine[i].qty, 10) > 0) {
        orderHasItems = true
        break
      }
    }
  }
  return orderHasItems
}
