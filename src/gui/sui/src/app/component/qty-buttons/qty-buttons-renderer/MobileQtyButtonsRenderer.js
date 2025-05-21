import React, { Component } from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'

import { I18N } from '3s-posui/core'
import { FlexChild, FlexGrid } from '3s-widgets'
import Button from '../../../../component/action-button/Button'
import ButtonGrid from '../../button-grid/ButtonGrid'


const styles = (theme) =>({
  qtyButtonSelected: {
    color: theme.fontColor,
    textShadow: 'none'
  }
})

export default class MobileQtyButtonsRenderer extends Component {
  render() {
    const { classes, value } = this.props
    const buttons = []
    const otherSelected = value
    buttons.push((
      <Button
        key={`other_qty_${otherSelected}`}
        className={`${classes.qtyButton} test_MobileQtyButtonsRenderer_QTY`}
        style={{ ...((otherSelected) ? styles.qtyButtonSelected : {}) }}
        executeAction={['requestQuantity']}
        onActionFinish={(response) => this.props.handleAnyQtyButton(response)}
        blockOnActionRunning={true}
      >
        {value}
      </Button>
    ))
    const qtyButtons = _.zipObject(_.range(1), buttons)

    return (
      <div className={classes.container}>
        <FlexGrid direction={'row'}>
          <FlexChild>
            <div className={classes.qtyCont}>
              <div className={classes.qtyTitle}>
                <I18N id="$QUANTITY" defaultMessage="Quantity"/>
              </div>
              <div className={classes.qtyGridCont}>
                <ButtonGrid
                  className={classes.qtyGridPadding}
                  direction="column"
                  cols={1}
                  rows={1}
                  buttons={qtyButtons}
                />
              </div>
            </div>
          </FlexChild>
        </FlexGrid>
      </div>
    )
  }
}

MobileQtyButtonsRenderer.propTypes = {
  classes: PropTypes.object,
  value: PropTypes.number.isRequired,
  handleAnyQtyButton: PropTypes.func,
  handleQtyButtonClicked: PropTypes.func
}
