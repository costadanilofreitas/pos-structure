import React, { Component } from 'react'
import PropTypes from 'prop-types'
import TableOrderHeader from '../table-order-header'
import CustomSalePanel from '../../../custom-sale-panel'

export default class MobileTableOrderDetails extends Component {
  constructor(props) {
    super(props)

    this.state = {
      showingDetails: false
    }

    this.handleOnExpand = this.handleOnExpand.bind(this)
  }

  render() {
    const { order, currentTime, tableStatus } = this.props
    const classes = this.props.classes || {}

    const rootContainerClass = this.state.showingDetails ? classes.rootContainerWithDetails : classes.rootContainer
    const orderContainerClass = this.state.showingDetails ? classes.orderContainerWithDetails : classes.orderContainer

    return (
      <div className={rootContainerClass}>
        <div className={orderContainerClass} key={`container_${order['@attributes'].orderId}`}>
          <TableOrderHeader
            order={order}
            tableStatus={tableStatus}
            currentTime={currentTime}
            showExpand={true}
            isExpanded={this.state.showingDetails}
            onExpand={this.handleOnExpand}
            onOrderChange={this.props.onOrderChange}
          />
        </div>
        {this.state.showingDetails && (
          <div className={classes.salePanelContainer}>
            <div className={classes.salePanelOuterContainer}>
              <CustomSalePanel
                key={`sp_${order['@attributes'].orderId}`}
                showSummary={false}
                showSummaryDue={false}
                showHeader={false}
                showHoldAndFire={true}
                customOrder={order}
                styleOverflow={true}
              />
            </div>
          </div>
        )}
      </div>
    )
  }

  handleOnExpand() {
    this.setState({ showingDetails: !this.state.showingDetails })
  }
}

MobileTableOrderDetails.propTypes = {
  order: PropTypes.object,
  tableStatus: PropTypes.number.isRequired,
  currentTime: PropTypes.object,
  onOrderChange: PropTypes.func,
  classes: PropTypes.object
}
