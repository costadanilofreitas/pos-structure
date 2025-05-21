import React from 'react'
import PropTypes from 'prop-types'
import { FlexChild, FlexGrid } from '3s-widgets'

import TableDetails from '../../../component/table-details'
import TableActions from '../../../component/table-actions'
import TableOrders from '../../../component/table-orders'
import { findChildByType } from '../../../../util/renderUtil'
import withMirror from '../../../util/withMirror'

function DesktopSelectedTableRenderer({ mirror, children }) {
  const direction = mirror ? 'row-reverse' : 'row'

  return (
    <FlexGrid direction={direction}>
      <FlexChild size={1}>
        <FlexGrid direction={'column'}>
          <FlexChild size={5}>
            {findChildByType(children, TableDetails)}
          </FlexChild>
          <FlexChild size={6}>
            {findChildByType(children, TableActions)}
          </FlexChild>
        </FlexGrid>
      </FlexChild>
      <FlexChild size={2}>
        {findChildByType(children, TableOrders)}
      </FlexChild>
    </FlexGrid>
  )
}

DesktopSelectedTableRenderer.propTypes = {
  mirror: PropTypes.bool,
  children: PropTypes.oneOfType([PropTypes.array, PropTypes.object])
}

export default withMirror(DesktopSelectedTableRenderer)
