import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'
import { FlexChild, FlexGrid } from '3s-widgets'

import { IconStyle } from '../../../../constants/commonStyles'
import TableOrderDetails from './table-order-details'
import ActionButton from '../../../../component/action-button/JssActionButton'
import WorkingModePropTypes from '../../../../prop-types/WorkingModePropTypes'

const PAGE_SIZE = 6

export default class DesktopTableOrdersRenderer extends Component {
  constructor(props) {
    super(props)

    this.state = {
      page: 0
    }

    this.handleOnPreviousClick = this.handleOnPreviousClick.bind(this)
    this.handleOnClickNext = this.handleOnClickNext.bind(this)
  }

  render() {
    let begin = 0
    let end = 0

    let filteredOrders = this.props.orders
    if (filteredOrders.length > PAGE_SIZE) {
      end = ((this.state.page + 1) * PAGE_SIZE)
      begin = ((this.state.page + 1) * PAGE_SIZE) - PAGE_SIZE
      if (begin < 0) {
        begin = 0
      }
      filteredOrders = filteredOrders.slice(begin, end)
    }

    const { classes, workingMode } = this.props

    return (
      <FlexGrid direction={'column'} className={classes.ordersContainer}>
        <FlexChild size={10}>
          {filteredOrders.map((order, index) => (
            <TableOrderDetails
              key={`tod${index}`}
              order={order}
              currentTime={this.props.currentTime}
              onOrderChange={this.props.onOrderChange}
              onOrderCancel={this.props.onOrderCancel}
              onOrderPrint={this.props.onOrderPrint}
              tableStatus={this.props.status}
              workingMode={workingMode}
            />))
          }
        </FlexChild>
        <FlexChild size={1} outerClassName={classes.buttonsContainer}>
          <div className={classes.buttonContainer}>
            <ActionButton
              className={`${classes.button} ${classes.previousButton}`}
              classNamePressed={`${classes.buttonPressed} ${classes.previousButton}`}
              classNameDisabled={`${classes.buttonDisabled} ${classes.previousButton}`}
              key="previous"
              onClick={this.handleOnPreviousClick}
              disabled={(this.state.page === 0)}
              blockOnActionRunning={true}
            >
              <i className="fas fa-chevron-left" aria-hidden="true" style={{ margin: '0.5vh' }}/>
              <I18N id="$PREVIOUS"/>
            </ActionButton>
          </div>
          <div className={classes.buttonContainer}>
            <ActionButton
              className={`${classes.button} ${classes.nextButton}`}
              classNamePressed={`${classes.buttonPressed} ${classes.nextButton}`}
              classNameDisabled={`${classes.buttonDisabled} ${classes.nextButton}`}
              key="next"
              onClick={this.handleOnClickNext}
              disabled={((this.state.page + 1) * PAGE_SIZE >= this.props.orders.length)}
              blockOnActionRunning={true}
            >
              <I18N id="$NEXT"/>
              <IconStyle
                className="fas fa-chevron-right"
                aria-hidden="true"
                disabled={((this.state.page + 1) * PAGE_SIZE >= this.props.orders.length)}
              />
            </ActionButton>
          </div>
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
    if ((this.state.page + 1) * PAGE_SIZE < this.props.orders.length) {
      this.setState({ page: this.state.page + 1 })
    }
  }
}

DesktopTableOrdersRenderer.propTypes = {
  orders: PropTypes.array,
  status: PropTypes.number.isRequired,
  currentTime: PropTypes.object,
  workingMode: WorkingModePropTypes,
  onOrderChange: PropTypes.func,
  onOrderCancel: PropTypes.func,
  onOrderPrint: PropTypes.func,
  classes: PropTypes.object
}
