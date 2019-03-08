import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { Button } from 'posui/button'
import { ButtonGrid } from 'posui/widgets'
import injectSheet, { jss } from 'react-jss'
import _ from 'lodash'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = (theme) => ({
  qtyButton: {
    backgroundColor: 'white',
    border: '1px solid #cccccc',
    ...(theme.qtyButton || {})
  },
  qtyButtonSelected: {
    color: 'black',
    backgroundColor: '#eeeeee',
    border: '1px solid #cccccc',
    textShadow: 'none',
    ...(theme.qtyButtonSelected || {})
  },
  qtyGridPadding: {
    boxSizing: 'border-box',
    '& .button-grid-cell-root': {
      padding: '0.2vh 0.6vh'
    },
    ...(theme.qtyGridPadding || {})
  }
})

class QtyButtons extends PureComponent {

  handleQtyButtonClicked = (qty) => {
    this.props.onChange(qty)
  }

  handleAnyQtyButton = (response) => {
    const qty = parseInt(response, 10)
    if (qty > 0) {
      this.props.onChange(qty)
    }
  }

  render() {
    const { classes, value } = this.props
    const buttons = _.map(_.range(1, 11), (qty) => {
      const selected = (qty === value)
      const currentClass = (selected) ? classes.qtyButtonSelected : ''
      return (
        <Button
          key={`${qty}_${selected}`}
          className={`${classes.qtyButton} ${currentClass}`}
          rounded={true}
          onClick={() => this.handleQtyButtonClicked(qty)}
          blockOnActionRunning={true}
        >{qty}</Button>
      )
    })
    const otherSelected = ((value || 0) > 10)
    const label = (otherSelected) ? value : '#'
    const currentClass = (otherSelected) ? classes.qtyButtonSelected : ''
    buttons.push((
      <Button
        key={`other_qty_${otherSelected}`}
        className={`${classes.qtyButton} ${currentClass}`}
        rounded={true}
        executeAction={['requestQuantity']}
        onActionFinish={(response) => this.handleAnyQtyButton(response)}
        blockOnActionRunning={true}
      >{label}</Button>
    ))
    const qtyButtons = _.zipObject(_.range(11), buttons)
    return (
      <ButtonGrid
        className={classes.qtyGridPadding}
        direction="column"
        cols={1}
        rows={11}
        buttons={qtyButtons}
      />
    )
  }
}

QtyButtons.propTypes = {
  /**
   * Injected classes
   * @ignore
   */
  classes: PropTypes.object,
  /**
   * Quantity value, to work as a controlled component
   */
  value: PropTypes.number.isRequired,
  /**
   * Called when the users sets a quantity for next sale, either by clicking on one of the buttons
   * from 1 to 10, or by entering a quantity on the calculator.
   */
  onChange: PropTypes.func.isRequired
}

export default injectSheet(styles)(QtyButtons)
