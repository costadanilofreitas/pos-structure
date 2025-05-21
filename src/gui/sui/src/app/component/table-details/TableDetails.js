import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { getStatusLabel, TableStatus } from '../../model/TableStatus'
import TableType from '../../model/TableType'
import TablePropTypes from '../../../prop-types/TablePropTypes'
import TableDetailsRenderer from './renderer'


export default class TableDetails extends Component {
  constructor(props) {
    super(props)

    this.interval = null
    this.state = {
      time: props.getCurrentDate()
    }
  }

  render() {
    const props = this.props

    const table = props.selectedTable
    let totalAmount = 0
    let numberOfOrders = 0
    if (props.selectedTable && props.selectedTable.orders && table.status !== TableStatus.Available) {
      props.selectedTable.orders.forEach(order => {
        totalAmount += order.totalGross + order.discountAmount
        numberOfOrders += 1
      })
    }

    let operatorInfo = '-'
    if (table.userId && table.status !== TableStatus.Available) {
      if (props.userList != null && props.userList[table.userId] != null) {
        operatorInfo = `${table.userId} / ${props.userList[table.userId].LongName}`
      } else {
        operatorInfo = table.userId
      }
    }

    const tableDetails = [
      {
        id: 'status',
        value: getStatusLabel(table.status),
        compact: true
      },
      {
        id: 'sector',
        value: table.sector
      },
      {
        id: 'operator',
        value: operatorInfo,
        compact: true
      },
      {
        id: 'numberOfOrders',
        value: numberOfOrders
      },
      {
        id: 'tableAmount',
        value: totalAmount,
        compact: true
      },
      {
        id: 'numberOfSeats',
        value: table.serviceSeats && table.status !== TableStatus.Available ? table.serviceSeats : '-',
        compact: true
      },
      {
        id: 'averageTicket',
        value: totalAmount / table.serviceSeats
      },
      {
        id: 'timeOpened',
        value: table.startTS && table.status !== TableStatus.Available ?
          props.getCurrentDate().getTime() - table.startTS.getTime() : '-',
        compact: true
      },
      {
        id: 'lastUpdateTime',
        value: table.lastUpdateTS && table.status !== TableStatus.Available ?
          props.getCurrentDate().getTime() - table.lastUpdateTS.getTime() : '-',
        compact: true
      }
    ]

    if (table.linkedTables && table.linkedTables.length > 0) {
      tableDetails.push({
        id: 'linkedTables',
        value: table.linkedTables
      })
    }

    if (table.specialCatalog) {
      tableDetails.push({
        id: 'specialCatalog',
        value: table.specialCatalog
      })
    }

    const tableInfo = {
      type: table.type,
      number: TableType.Seat === table.type ? table.id : table.tabNumber,
      details: tableDetails
    }

    return <TableDetailsRenderer tableInfo={tableInfo} showMobile={props.showMobile} compact={props.compact}/>
  }

  componentDidMount() {
    this.interval = setInterval(() => {
      this.setState({ time: this.props.getCurrentDate() })
    }, 1000)
  }

  componentWillUnmount() {
    clearInterval(this.interval)
  }
}

TableDetails.propTypes = {
  selectedTable: TablePropTypes,
  getCurrentDate: PropTypes.func,
  showMobile: PropTypes.bool,
  compact: PropTypes.bool,
  classes: PropTypes.object,
  userList: PropTypes.object
}
