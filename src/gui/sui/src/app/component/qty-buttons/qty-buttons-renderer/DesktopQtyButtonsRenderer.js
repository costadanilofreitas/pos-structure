import React, { Component } from 'react'
import _ from 'lodash'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'
import Button from '../../../../component/action-button/Button'
import ButtonGrid from '../../button-grid/ButtonGrid'

export default class DesktopQtyButtonsRenderer extends Component {
  render() {
    const { classes, value } = this.props
    let selectedBtnClass
    const buttons = _.map(_.range(1, 11), (qty) => {
      const selected = (qty === value)
      selectedBtnClass = selected ? classes.qtyButtonSelected : classes.qtyButtonUnselected
      return (
        <Button
          key={`${qty}_${selected}`}
          className={`${classes.qtyButton} ${selectedBtnClass} test_QtyButtonsRenderer_${qty}`}
          onClick={() => this.props.handleQtyButtonClicked(qty)}
          blockOnActionRunning={true}
        >
          {qty}
        </Button>
      )
    })
    const otherSelected = ((value || 0) > 10)
    const label = (otherSelected) ? value : '#'
    selectedBtnClass = otherSelected ? classes.qtyButtonSelected : classes.qtyButtonUnselected
    buttons.push((
      <Button
        key={`other_qty_${otherSelected}`}
        className={`${classes.qtyButton} ${selectedBtnClass} test_QtyButtonsRenderer_SELECTOR`}
        executeAction={['requestQuantity']}
        onActionFinish={(response) => this.props.handleAnyQtyButton(response)}
        blockOnActionRunning={true}
      >
        {label}
      </Button>
    ))
    const qtyButtons = _.zipObject(_.range(11), buttons)
    return (
      <div className={classes.qtyCont}>
        <div className={classes.qtyTitle}>
          <I18N id="$QUANTITY" defaultMessage="Quantity"/>
        </div>
        <div className={classes.qtyGridCont}>
          <ButtonGrid
            className={classes.qtyGridPadding}
            direction="column"
            cols={1}
            rows={11}
            buttons={qtyButtons}
          />
        </div>
      </div>
    )
  }
}

DesktopQtyButtonsRenderer.propTypes = {
  classes: PropTypes.object,
  value: PropTypes.number.isRequired,
  handleAnyQtyButton: PropTypes.func,
  handleQtyButtonClicked: PropTypes.func
}
