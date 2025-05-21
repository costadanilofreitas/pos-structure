import React from 'react'
import PropTypes from 'prop-types'

import TableDetails from '../../component/table-details'
import TableActions from '../../component/table-actions'
import TableOrders from '../../component/table-orders'
import SelectedTableRenderer from './renderer'
import TablePropTypes from '../../../prop-types/TablePropTypes'


export default function SelectedTableScreen({ selectedTable, setSeatScreen, mirror }) {
  return (
    <SelectedTableRenderer selectedTable={selectedTable} mirror={mirror}>
      <TableDetails selectedTable={selectedTable}/>
      <TableActions selectedTable={selectedTable} setSeatScreen={setSeatScreen}/>
      <TableOrders orders={selectedTable.orders} status={selectedTable.status} table={selectedTable}/>
    </SelectedTableRenderer>
  )
}

SelectedTableScreen.propTypes = {
  selectedTable: TablePropTypes.isRequired,
  mirror: PropTypes.bool.isRequired,
  setSeatScreen: PropTypes.func
}
