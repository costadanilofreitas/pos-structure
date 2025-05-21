import React, { Component } from 'react'
import PropTypes from 'prop-types'

import TableListScreen from '../table-list-screen'
import SelectedTableScreen from '../selected-table-screen'
import EditSeatScreen from '../edit-seats-screen'
import { TableStatus } from '../../model/TableStatus'
import TenderScreen from '../tender-screen'
import TablePropTypes from '../../../prop-types/TablePropTypes'


export default class TableScreen extends Component {
  constructor(props) {
    super(props)

    this.state = {
      showEditSeatScreen: false
    }
    this.setEditSeatState = this.setEditSeatState.bind(this)
  }

  static getDerivedStateFromProps(props) {
    if (props.selectedTable != null && !props.showTableInfo) {
      if (props.selectedTable.status === TableStatus.Totalized) {
        return { showEditSeatScreen: false }
      }
    }
    return null
  }

  getScreen() {
    const { selectedTable, showTableInfo } = this.props
    const setSeatScreen = (value) => this.setEditSeatState(value)
    if (selectedTable != null && !showTableInfo) {
      if (selectedTable.status === TableStatus.Totalized) {
        return <TenderScreen order={selectedTable.orders[0]} />
      }
      if (this.state.showEditSeatScreen === true) {
        return <EditSeatScreen selectedTable={selectedTable} setSeatScreen={setSeatScreen} />
      }
      return <SelectedTableScreen selectedTable={selectedTable} setSeatScreen={setSeatScreen} />
    }
    return <TableListScreen selectedTable={selectedTable} />
  }

  setEditSeatState(value) {
    this.setState({ showEditSeatScreen: value })
  }

  render() {
    return (this.getScreen())
  }
}

TableScreen.propTypes = {
  selectedTable: TablePropTypes,
  showTableInfo: PropTypes.bool
}
