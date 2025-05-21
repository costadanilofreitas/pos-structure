import React from 'react'
import PropTypes from 'prop-types'

import { FlexChild, FlexGrid } from '3s-widgets'

import { findChildByType } from '../../../../../util/renderUtil'
import TableActions from '../../../../component/table-actions'
import withState from '../../../../../util/withState'
import OrderTotal from '../../../../component/order-total'
import TableDetails from '../../../../component/table-details'
import OrderTenders from '../../../../component/order-tenders'
import TablePropTypes from '../../../../../prop-types/TablePropTypes'
import OrderFunctions from '../../../../component/order-functions'


function MobileTenderScreenRenderer(props) {
  const { children, selectedTable } = props
  return (
    <FlexGrid direction={'column'}>
      {selectedTable != null
        ?
        <FlexChild size={1}>
          { findChildByType(children, TableDetails) }
        </FlexChild>
        : null
      }
      <FlexChild size={selectedTable != null ? 7 : 8}>
        {findChildByType(children, OrderTenders)}
      </FlexChild>
      <FlexChild size={1}>
        { findChildByType(children, OrderTotal) }
      </FlexChild>
      <FlexChild size={2}>
        { findChildByType(children, selectedTable != null ? TableActions : OrderFunctions) }
      </FlexChild>
    </FlexGrid>
  )
}

MobileTenderScreenRenderer.propTypes = {
  children: PropTypes.oneOfType([PropTypes.array, PropTypes.object]),
  selectedTable: TablePropTypes
}

export default withState(MobileTenderScreenRenderer, 'selectedTable')
