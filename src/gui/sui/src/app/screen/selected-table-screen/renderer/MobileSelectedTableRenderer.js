import React from 'react'
import PropTypes from 'prop-types'

import { FlexChild, FlexGrid } from '3s-widgets'

import TableDetails from '../../../component/table-details'
import TableActions from '../../../component/table-actions'
import TableOrders from '../../../component/table-orders'
import { findChildByType } from '../../../../util/renderUtil'


export default function MobileSelectedTableRenderer({ children }) {
  return (
    <FlexGrid direction={'column'}>
      <FlexChild size={1}>
        {findChildByType(children, TableDetails)}
      </FlexChild>
      <FlexChild size={8}>
        {findChildByType(children, TableOrders)}
      </FlexChild>
      <FlexChild size={2}>
        {findChildByType(children, TableActions)}
      </FlexChild>
    </FlexGrid>
  )
}

MobileSelectedTableRenderer.propTypes = {
  children: PropTypes.oneOfType([PropTypes.array, PropTypes.object])
}
