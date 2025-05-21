import React from 'react'
import PropTypes from 'prop-types'

import TableSeatsList from '../../component/table-seats-list'

export default function EditSeatsScreen({ selectedTable, setSeatScreen }) {
  return <TableSeatsList selectedTable={selectedTable} setSeatScreen={setSeatScreen}/>
}

EditSeatsScreen.propTypes = {
  selectedTable: PropTypes.object.isRequired,
  setSeatScreen: PropTypes.func
}
