import React, { Component } from 'react'
import PropTypes from 'prop-types'
import QtyButtonsRenderer from './qty-buttons-renderer/QtyButtonsRenderer'
import { shallowIgnoreEquals } from '../../../util/renderUtil'


class QtyButtons extends Component {
  constructor(props) {
    super(props)

    this.handleQtyButtonClicked = this.handleQtyButtonClicked.bind(this)
    this.handleAnyQtyButton = this.handleAnyQtyButton.bind(this)
  }

  shouldComponentUpdate(nextProps) {
    return !shallowIgnoreEquals(this.props, nextProps, 'actionRunning', 'classes')
  }

  handleQtyButtonClicked = (qty) => {
    this.props.onChange(qty)
  }

  handleAnyQtyButton = (response) => {
    const qty = (response != null) ? parseFloat(response.data) : 0
    if (qty > 0) {
      this.props.onChange(qty)
    }
  }

  render() {
    return (
      <QtyButtonsRenderer
        handleQtyButtonClicked={this.handleQtyButtonClicked}
        handleAnyQtyButton={this.handleAnyQtyButton}
        value={this.props.value}
      />
    )
  }
}

QtyButtons.propTypes = {
  value: PropTypes.number.isRequired,
  onChange: PropTypes.func.isRequired
}

export default QtyButtons
