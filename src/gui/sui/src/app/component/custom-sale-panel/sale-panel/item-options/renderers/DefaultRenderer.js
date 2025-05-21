import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { FlexGrid } from '3s-widgets'
import ActionButton from '../../../../../../component/action-button'


class DefaultRenderer extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    const { classes, itemQuantity, lineNumber, changeQuantity, deleteLines, showModifierScreen } = this.props

    return (
      <FlexGrid direction={'row'} className={classes.itemBox}>
        <ActionButton executeAction={() => this.props.changeQuantity(lineNumber, itemQuantity, false)}>
          <i className="fa fa-minus" aria-hidden="true" style={{ margin: '0.5vh' }}/><br/>
        </ActionButton>

        <ActionButton
          executeAction={() => changeQuantity(lineNumber, itemQuantity, true)}
        >
          <i className="fa fa-plus" aria-hidden="true" style={{ margin: '0.5vh' }}/><br/>
        </ActionButton>

        <ActionButton
          executeAction={() => deleteLines([lineNumber])}
        >
          <i className="fa fa-times" aria-hidden="true" style={{ margin: '0.5vh' }}/><br/>
        </ActionButton>

        <ActionButton
          executeAction={() => showModifierScreen()}
        >
          <i className="fas fa-exchange-alt" aria-hidden="true" style={{ margin: '0.5vh' }}/><br/>
        </ActionButton>
      </FlexGrid>
    )
  }
}

DefaultRenderer.propTypes = {
  classes: PropTypes.object,
  itemQuantity: PropTypes.number,
  lineNumber: PropTypes.number,
  changeQuantity: PropTypes.func,
  deleteLines: PropTypes.func,
  showModifierScreen: PropTypes.func
}

export default DefaultRenderer
