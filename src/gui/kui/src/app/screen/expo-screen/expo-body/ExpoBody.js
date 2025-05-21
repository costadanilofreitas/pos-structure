import React, { Component } from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'

import { FlexChild, FlexGrid } from '3s-widgets'
import ExpoBodyContainer from './StyledExpoBody'
import KdsCell from '../expo-cell'
import { deepEquals } from '../../../../util/renderUtil'


function rowsChanged(previousKdsModel, nextKdsModel) {
  return previousKdsModel.layout.rows !== nextKdsModel.layout.rows
}

function columnsChanged(previousKdsModel, nextKdsModel) {
  return previousKdsModel.layout.cols !== nextKdsModel.layout.cols
}

function hasKdsModel(previousKdsModel, nextKdsModel) {
  return previousKdsModel !== null && nextKdsModel !== null
}

function kdsModelHasLayout(previousKdsModel, nextKdsModel) {
  return previousKdsModel.layout !== null && nextKdsModel.layout !== null
}

function dimensionsChanged(props, nextProps) {
  const previousKdsModel = props.kdsModel
  const nextKdsModel = nextProps.kdsModel

  if (!hasKdsModel(previousKdsModel, nextKdsModel)) {
    return false
  }

  if (!kdsModelHasLayout(previousKdsModel, nextKdsModel)) {
    return false
  }

  return rowsChanged(previousKdsModel, nextKdsModel) || columnsChanged(previousKdsModel, nextKdsModel)
}

function getOrderId(order) {
  return order && order.attrs.order_id
}

function getOrderFromArrayByIndex(ordersArray, index) {
  return ordersArray[index] !== undefined && !_.isEmpty(ordersArray[index]) ? ordersArray[index] : null
}

export default class ExpoBody extends Component {
  constructor(props) {
    super(props)

    this.renderGrid = this.renderGrid.bind(this)
    this.renderCell = this.renderCell.bind(this)
    this.renderRow = this.renderRow.bind(this)
  }

  shouldComponentUpdate(nextProps) {
    if (dimensionsChanged(this.props, nextProps)) {
      return true
    }

    if (nextProps.currentOrder !== this.props.currentOrder) {
      return true
    }

    if (nextProps.paginationBlockSize !== this.props.paginationBlockSize) {
      return true
    }

    if (this.props.orders.length !== nextProps.orders.length) {
      return true
    } else if (nextProps.orders.length !== 0) {
      return !deepEquals(nextProps.orders, this.props.orders)
    }

    return false
  }

  renderGrid() {
    const { kdsModel } = this.props
    const rows = kdsModel.layout.rows

    const rowsElement = []
    for (let i = 0; i < rows; i++) {
      rowsElement[i] = this.renderRow(i)
    }

    return (
      <FlexGrid direction={'column'}>
        {rowsElement.map((row, rowIndex) => (
          <FlexChild key={`row-${rowIndex}` }>
            {row}
          </FlexChild>
        ))}
      </FlexGrid>
    )
  }

  renderRow(rowIndex) {
    const { kdsModel } = this.props
    const columns = kdsModel.layout.cols

    const colsElement = []
    for (let i = 0; i < columns; i++) {
      colsElement[i] = this.renderCell(rowIndex, i)
    }

    return (
      <FlexGrid direction={'row'}>
        {colsElement.map((col, colIndex) => (
          <FlexChild key={`column-${colIndex}`}>
            {col}
          </FlexChild>
        ))}
      </FlexGrid>
    )
  }

  renderCell(rowIndex, colIndex) {
    const { kdsModel, paginationBlockSize, currentOrder, orders } = this.props
    if (orders.length === 0) {
      return null
    }

    const cols = kdsModel.layout.cols
    const index = (rowIndex * cols) + colIndex + paginationBlockSize
    const order = getOrderFromArrayByIndex(orders, index)
    const currentOrderId = orders[currentOrder] != null ? orders[currentOrder].attrs.order_id : 0

    if (!order) {
      return null
    }
    return (
      <KdsCell
        kdsModel={kdsModel}
        order={order}
        row={rowIndex}
        col={colIndex}
        index={index}
        selected={currentOrderId === getOrderId(order)}
      />
    )
  }

  render() {
    return (
      <ExpoBodyContainer>
        {this.renderGrid()}
      </ExpoBodyContainer>
    )
  }
}

ExpoBody.propTypes = {
  kdsModel: PropTypes.object,
  orders: PropTypes.array,
  currentOrder: PropTypes.number,
  paginationBlockSize: PropTypes.number
}
