import React, { Component } from 'react'
import { connect } from 'react-redux'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'
import { FlexChild, FlexGrid } from '3s-widgets'

import { IconStyle } from '../../../constants/commonStyles'
import SeatItems from './seat-items'
import TableSeatsActions from '../table-seats-actions'
import DialogType from '../../../constants/DialogType'
import ActionButton from '../../../component/action-button/JssActionButton'
import TableDetails from '../table-details'
import MessageBusPropTypes from '../../../prop-types/MessageBusPropTypes'


class TableSeatList extends Component {
  constructor(props) {
    super(props)

    this.pageSize = this.props.mobile === true ? 2 : 6
    this.state = {
      page: 0,
      selectedSaleLines: [],
      seatBeingChanged: null,
      enabledToReorganizeItems: false
    }

    this.handleOnSaleLineSelected = this.handleOnSaleLineSelected.bind(this)
    this.handleOnClick = this.handleOnClick.bind(this)
    this.handleOnSeatSelect = this.handleOnSeatSelect.bind(this)
    this.handleOnPreviousClick = this.handleOnPreviousClick.bind(this)
    this.handleOnClickNext = this.handleOnClickNext.bind(this)
    this.handleOnSplitItems = this.handleOnSplitItems.bind(this)
    this.handleOnMergeItems = this.handleOnMergeItems.bind(this)
    this.handleOnChangeSeats = this.handleOnChangeSeats.bind(this)
    this.handleOnChangeEnabledToReorganizeItems = this.handleOnChangeEnabledToReorganizeItems.bind(this)
  }

  render() {
    const { enabledToReorganizeItems } = this.state
    const { classes, mirror, mobile } = this.props

    let begin = 0
    let end = this.props.selectedTable.serviceSeats

    if (this.props.selectedTable.serviceSeats > this.pageSize) {
      end = ((this.state.page + 1) * this.pageSize)
      if (end > this.props.selectedTable.serviceSeats) {
        end = this.props.selectedTable.serviceSeats
      }
      begin = ((this.state.page + 1) * this.pageSize) - this.pageSize
      if (begin < 0) {
        begin = 0
      }
    }

    const filteredSeats = []
    for (let i = begin + 1; i <= end; i++) {
      filteredSeats.push(i)
    }

    const itemsPerSeat = this.buildItemsPerSeat(this.props.selectedTable)
    const singleSeatContainer = mobile === true ? classes.singleSeatContainerMobile : classes.singleSeatContainerDesktop

    const direction = mirror ? 'row-reverse' : 'row'
    return (
      <FlexGrid direction={direction}>
        <FlexChild size={1}>
          <FlexGrid direction={'column'}>
            <FlexChild size={1}>
              <TableDetails selectedTable={this.props.selectedTable} showMobile={true}/>
            </FlexChild>
            <FlexChild size={7}>
              {this.buildSeatItems(0, itemsPerSeat, this.props.selectedTable.id)}
            </FlexChild>
            <FlexChild size={3}>
              <TableSeatsActions
                {...this.props}
                enabledToReorganizeItems={enabledToReorganizeItems}
                onMergeItems={this.handleOnMergeItems}
                onSplitItems={this.handleOnSplitItems}
                onChangeSeats={this.handleOnChangeSeats}
                onChangeEnabledToReorganizeItems={this.handleOnChangeEnabledToReorganizeItems}
              />
            </FlexChild>
          </FlexGrid>
        </FlexChild>
        <FlexChild size={mobile === true ? 1 : 2}>
          <FlexGrid direction={'column'} className={classes.ordersContainer}>
            <FlexChild size={10}>
              {filteredSeats.map(seat => {
                return (
                  <div key={`seatContainer${seat}`} className={singleSeatContainer}>
                    {this.buildSeatItems(seat, itemsPerSeat, this.props.selectedTable.id)}
                  </div>
                )
              })}
            </FlexChild>
            <FlexChild size={1} outerClassName={classes.buttonsContainer}>
              <div className={classes.buttonContainer}>
                <ActionButton
                  className={`${classes.button} ${classes.previousButton} test_TableSeatsList_PREVIOUS`}
                  classNamePressed={`${classes.buttonPressed} ${classes.previousButton}`}
                  classNameDisabled={`${classes.buttonDisabled} ${classes.previousButton}`}
                  key="previous"
                  onClick={this.handleOnPreviousClick}
                  disabled={(this.state.page === 0)}
                >
                  <i className="fas fa-chevron-left" aria-hidden="true" style={{ margin: '0.5vh' }}/>
                  <I18N id="$PREVIOUS"/>
                </ActionButton>
              </div>
              <div className={classes.buttonContainer}>
                <ActionButton
                  className={`${classes.button} ${classes.nextButton} test_TableSeatsList_NEXT`}
                  classNamePressed={`${classes.buttonPressed} ${classes.nextButton}`}
                  classNameDisabled={`${classes.buttonDisabled} ${classes.nextButton}`}
                  key="next"
                  onClick={this.handleOnClickNext}
                  disabled={((this.state.page + 1) * this.pageSize >= this.props.selectedTable.serviceSeats)}
                >
                  <I18N id="$NEXT"/>
                  <IconStyle className="fas fa-chevron-right" aria-hidden="true"/>
                </ActionButton>
              </div>
            </FlexChild>
          </FlexGrid>
        </FlexChild>
      </FlexGrid>
    )
  }

  handleOnPreviousClick() {
    if (this.state.page > 0) {
      this.setState({ page: this.state.page - 1 })
    }
  }

  handleOnClickNext() {
    if ((this.state.page + 1) * this.pageSize < this.props.selectedTable.serviceSeats) {
      this.setState({ page: this.state.page + 1 })
    }
  }

  handleOnMergeItems() {
    this.props.msgBus.syncAction('do_merge_items', JSON.stringify(this.state.selectedSaleLines))
      .then(response => {
        if (response.ok && response.data !== 'False' && response.data !== '') {
          this.setState({ selectedSaleLines: [] })
        }
      })
  }

  handleOnSplitItems() {
    this.props.msgBus.syncAction('do_split_items', JSON.stringify(this.state.selectedSaleLines))
      .then(response => {
        if (response.ok && response.data !== 'False' && response.data !== '') {
          this.setState({ selectedSaleLines: [] })
        }
      })
  }

  handleOnChangeSeats(selectedSaleLines) {
    this.props.msgBus.syncAction('do_change_table_seats', JSON.stringify(parseInt(selectedSaleLines, 10)))
  }

  handleOnSaleLineSelected(seat, saleLine) {
    if (seat !== 0 && !this.isAuthorized()) {
      return
    }

    if (this.isTheCurrentSelectedSaleLine(saleLine)) {
      this.removeSaleLine(saleLine)
    } else if (this.sameSeatSelected(seat)) {
      this.addSaleLine(saleLine)
    } else {
      this.notifySaleLineChange(seat)
    }
  }

  handleOnClick(seat) {
    if (seat !== 0 && !this.isAuthorized()) {
      return
    }

    if (this.hasSaleLineSelected() && !this.sameSeatSelected(seat)) {
      this.notifySaleLineChange(seat)
    }
  }

  handleOnSeatSelect(newSeat) {
    if (newSeat != null) {
      const newActiveList = this.state.displayedSeats.map(seat => {
        if (seat === this.seatBeingChanged) {
          return parseInt(this.hiddenSeats.ids[newSeat], 10)
        }
        return seat
      })

      this.setState({ displayedSeats: newActiveList })
    }
  }

  handleOnChangeEnabledToReorganizeItems() {
    if (!this.state.enabledToReorganizeItems) {
      this.props.msgBus.syncAction('get_manager_authorization')
        .then(response => {
          if (response.ok && response.data !== 'False' && response.data !== '') {
            this.setState({ enabledToReorganizeItems: true })
          } else {
            this.setState({ enabledToReorganizeItems: false })
          }
        })
    } else {
      this.setState({ enabledToReorganizeItems: false })
    }
  }

  isAuthorized() {
    if (!this.state.enabledToReorganizeItems) {
      this.props.showDialog({
        type: DialogType.Alert,
        onClose: function () {},
        message: '$NECESSARY_AUTHORIZATION'
      })
      return false
    }

    return true
  }

  buildSeatItems(seat, itemsPerSeat, tableId) {
    return (
      <SeatItems
        key={`seat${seat}`}
        seat={seat}
        saleLines={itemsPerSeat[seat]}
        tableId={tableId}
        selectedSaleLines={this.state.selectedSaleLines}
        onSaleLineSelect={(saleLine) => this.handleOnSaleLineSelected(seat, saleLine)}
        onClick={() => this.handleOnClick(seat)}
        setSeatScreen={this.props.setSeatScreen}
      />
    )
  }

  buildItemsPerSeat(table) {
    const seatsLists = []
    for (let i = 0; i <= table.serviceSeats; i++) {
      seatsLists.push([])
    }

    this.fillSaleLineWithoutSeat(table)
    table.orders.forEach(order => {
      order.saleLines.forEach(saleLine => {
        let index = !saleLine.seat ? 0 : saleLine.seat
        if (index > table.serviceSeats) {
          index = 0
        }
        seatsLists[index].push({ orderId: order.orderId, ...saleLine })
      })
    })

    return seatsLists
  }

  fillSaleLineWithoutSeat(table) {
    table.orders.forEach(order => {
      const currentSaleLines = order.saleLines
      order.saleLines.forEach(saleLine => {
        if (saleLine.seat == null) {
          for (let i = 0; i < currentSaleLines.length; i++) {
            if (saleLine.lineNumber === currentSaleLines[i].lineNumber) {
              const saleLineItemId = saleLine.itemId
              if (`${currentSaleLines[i].itemId}.${currentSaleLines[i].partCode}` === saleLineItemId) {
                saleLine.seat = currentSaleLines[i].seat
                break
              }
            }
          }
        }
      })
    })
  }

  sameSeatSelected(seat) {
    if (this.state.selectedSaleLines.length === 0 || (seat === 0 && !this.state.selectedSaleLines[0].seat)) {
      return true
    }

    return this.state.selectedSaleLines[0].seat === seat
  }

  hasSaleLineSelected() {
    return this.state.selectedSaleLines.length > 0
  }

  isTheCurrentSelectedSaleLine(saleLine) {
    if (this.state.selectedSaleLines) {
      for (let i = 0; i < this.state.selectedSaleLines.length; i++) {
        if (this.state.selectedSaleLines[i].orderId === saleLine.orderId &&
            this.state.selectedSaleLines[i].lineNumber === saleLine.lineNumber &&
            this.state.selectedSaleLines[i].itemId === saleLine.itemId &&
            this.state.selectedSaleLines[i].partCode === saleLine.partCode) {
          return true
        }
      }
    }

    return false
  }

  addSaleLine(selectedSaleLine) {
    const selectedSaleLines = this.state.selectedSaleLines

    this.props.selectedTable.orders.forEach(order => {
      order.saleLines.forEach(saleLine => {
        const orderId = order.orderId

        if (selectedSaleLine.orderId === order.orderId && selectedSaleLine.lineNumber === saleLine.lineNumber) {
          const sl = saleLine
          sl.orderId = orderId
          selectedSaleLines.push(sl)
        }
      })
    })

    this.setState({ selectedSaleLines: selectedSaleLines })
  }

  removeSaleLine(saleLine) {
    const selectedSaleLines = this.state.selectedSaleLines
    const newSelection = this.state.selectedSaleLines

    for (let i = 0; i < selectedSaleLines.length; i++) {
      const selectedSaleLine = selectedSaleLines[i]
      if (selectedSaleLine.orderId === saleLine.orderId && selectedSaleLine.lineNumber === saleLine.lineNumber) {
        const saleLineToRemove = newSelection.indexOf(selectedSaleLine)
        newSelection.splice(saleLineToRemove, 1)
      }
    }

    this.setState({ selectedSaleLines: newSelection })
  }

  notifySaleLineChange(seat) {
    this.props.onLineChange(this.state.selectedSaleLines, seat)
    this.setState({ selectedSaleLines: [] })
  }
}

TableSeatList.propTypes = {
  classes: PropTypes.object,
  custom: PropTypes.object,
  msgBus: MessageBusPropTypes,
  selectedTable: PropTypes.object.isRequired,
  onLineChange: PropTypes.func.isRequired,
  showDialog: PropTypes.func,
  getMessage: PropTypes.func,
  setSeatScreen: PropTypes.func,
  mobile: PropTypes.bool,
  mirror: PropTypes.bool
}

function mapStateToProps(state) {
  return {
    custom: state.custom,
    themeName: (state.custom || {}).THEME || 'default',
    mobile: state.mobile
  }
}

export default connect(mapStateToProps, null)(TableSeatList)
