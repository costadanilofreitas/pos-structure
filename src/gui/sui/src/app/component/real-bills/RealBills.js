import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { FlexChild, FlexGrid } from '3s-widgets'

import { IconStyle, CommonStyledButton } from '../../../constants/commonStyles'
import TablePropTypes from '../../../prop-types/TablePropTypes'

function createBillButton(value, seats, disabled, onExecuteAction) {
  return (
    <CommonStyledButton
      className={`test_OrderTender_${value}`}
      key={`cash${value}`}
      executeAction={() => onExecuteAction(value)}
      disabled={disabled}
      border={true}
    >
      <IconStyle
        className="far fa-money-bill-alt fa-2x"
        aria-hidden="true"
        disabled={disabled}
      />
      <br/>
      {`${value},00`}
    </CommonStyledButton>
  )
}

export default class RealBills extends Component {
  constructor(props) {
    super(props)

    this.deviceType = null

    this.handleDeviceTypeResponse = this.handleDeviceTypeResponse.bind(this)
    this.handleExecuteAction = this.handleExecuteAction.bind(this)
  }

  render() {
    const { selectedSeats, disabled } = this.props
    const seats = selectedSeats || null

    return (
      <FlexGrid direction={'row'}>
        <FlexChild>
          {createBillButton(10, seats, disabled, this.handleExecuteAction)}
        </FlexChild>
        <FlexChild>
          {createBillButton(20, seats, disabled, this.handleExecuteAction)}
        </FlexChild>
        <FlexChild>
          {createBillButton(50, seats, disabled, this.handleExecuteAction)}
        </FlexChild>
        <FlexChild>
          {createBillButton(100, seats, disabled, this.handleExecuteAction)}
        </FlexChild>
      </FlexGrid>
    )
  }

  componentDidMount() {
    if (window.mwapi != null) {
      window.getDeviceTypeCallBackRealBills = this.handleDeviceTypeResponse

      window.mwapi.getDeviceType('getDeviceTypeCallBackRealBills')
    }
  }

  handleDeviceTypeResponse(resultCode, message, payload) {
    if (resultCode === '0') {
      this.deviceType = payload
    }
  }

  handleExecuteAction(value) {
    const { selectedSeats, selectedTable } = this.props
    const seats = selectedSeats || null

    let seatsStr = null
    if (seats && Object.keys(seats).length > 0) {
      seatsStr = Object.values(seats).join(',')
    }

    let executionAction
    if (selectedTable == null) {
      executionAction = ['doTender', value, 0, false, true, false, this.deviceType]
    } else {
      executionAction = ['do_table_tender', 0, value, null, seatsStr, null, this.deviceType]
    }

    return executionAction
  }
}

RealBills.propTypes = {
  selectedSeats: PropTypes.object.isRequired,
  disabled: PropTypes.bool,
  selectedTable: TablePropTypes
}
