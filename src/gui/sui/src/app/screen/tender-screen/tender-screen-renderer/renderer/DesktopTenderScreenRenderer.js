import React from 'react'
import PropTypes from 'prop-types'

import { FlexChild, FlexGrid } from '3s-widgets'
import { SalePanelContainer } from '../StyledTenderScreen'

import DeliveryInfoRenderer from './delivery-renderer/DeliveryInfoRenderer'
import themes from '../../../../../constants/themes'
import withState from '../../../../../util/withState'
import { findChildByType } from '../../../../../util/renderUtil'
import TableActions from '../../../../component/table-actions'
import TableDetails from '../../../../component/table-details'
import CustomSalePanel from '../../../../component/custom-sale-panel'
import OrderTenders from '../../../../component/order-tenders'
import TenderDivision from '../../../../component/tender-division'
import TablePropTypes from '../../../../../prop-types/TablePropTypes'
import OrderFunctions from '../../../../component/order-functions'
import MessageBusPropTypes from '../../../../../prop-types/MessageBusPropTypes'
import OrderPropTypes from '../../../../../prop-types/OrderPropTypes'
import { isLocalDelivery } from '../../../../../util/orderUtil'
import StaticConfigPropTypes from '../../../../../prop-types/StaticConfigPropTypes'


function DesktopTenderScreenRenderer(props) {
  const { children, selectedTable, msgBus, order, staticConfig } = props
  return (
    <FlexGrid direction={'row'}>
      <FlexChild style={{ background: themes[0].defaultBackground }}>
        <FlexGrid direction={'column'}>
          <FlexChild size={selectedTable != null ? 5 : 3}>
            {selectedTable != null
              ? findChildByType(children, TableDetails)
              : findChildByType(children, TenderDivision)
            }
          </FlexChild>
          {selectedTable == null &&
            <FlexChild size={5}>
              {isLocalDelivery(order) && staticConfig.deliveryAddress &&
                <DeliveryInfoRenderer order={order} msgBus={msgBus}/>
              }
            </FlexChild>
          }
          <FlexChild size={selectedTable != null ? 6 : 2}>
            {selectedTable != null
              ? findChildByType(children, TableActions)
              : findChildByType(children, OrderFunctions)
            }
          </FlexChild>
        </FlexGrid>
      </FlexChild>
      <FlexChild>
        <SalePanelContainer theme={themes[0]}>
          {findChildByType(children, CustomSalePanel)}
        </SalePanelContainer>
      </FlexChild>
      <FlexChild style={{ background: themes[0].defaultBackground }}>
        <FlexGrid direction={'column'}>
          <FlexChild>
            {findChildByType(children, OrderTenders)}
          </FlexChild>
        </FlexGrid>
      </FlexChild>
    </FlexGrid>
  )
}

DesktopTenderScreenRenderer.propTypes = {
  selectedTable: TablePropTypes,
  order: OrderPropTypes,
  staticConfig: StaticConfigPropTypes,
  children: PropTypes.oneOfType([PropTypes.array, PropTypes.object]),
  msgBus: MessageBusPropTypes
}

export default withState(DesktopTenderScreenRenderer, 'selectedTable')
