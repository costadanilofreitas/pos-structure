import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { FlexGrid } from '3s-widgets'
import { I18N } from '3s-posui/core'
import { CustomActionButton } from './StyledTotemRenderer'


class TotemRenderer extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    const { classes, itemQuantity, lineNumber, changeQuantity, deleteLines, showModifierScreen, onDelete } = this.props

    const deleteFunction = () => {
      deleteLines([lineNumber])
      onDelete()
    }

    return (
      <FlexGrid direction={'row'} className={classes.itemBox}>
        <CustomActionButton
          className={'test_TotemItemOptions_MINUS'}
          executeAction={() => itemQuantity > 1 ?
            this.props.changeQuantity(lineNumber, itemQuantity, false) : deleteFunction()
          }
        >
          <i className="fa fa-minus" aria-hidden="true" style={{ margin: '0.5vh' }}/>
          <br/>
          <I18N id={'$REMOVE'}/>
        </CustomActionButton>

        <CustomActionButton
          className={'test_TotemItemOptions_ADD'}
          executeAction={() => changeQuantity(lineNumber, itemQuantity, true)}
        >
          <i className="fa fa-plus" aria-hidden="true" style={{ margin: '0.5vh' }}/>
          <br/>
          <I18N id={'$ADD'}/>
        </CustomActionButton>

        <CustomActionButton
          className={'test_TotemItemOptions_MODIFY'}
          executeAction={() => showModifierScreen()}
        >
          <i className="fas fa-exchange-alt" aria-hidden="true" style={{ margin: '0.5vh' }}/>
          <br/>
          <I18N id={'$MODIFY'}/>
        </CustomActionButton>
      </FlexGrid>
    )
  }
}

TotemRenderer.propTypes = {
  classes: PropTypes.object,
  itemQuantity: PropTypes.number,
  lineNumber: PropTypes.number,
  changeQuantity: PropTypes.func,
  deleteLines: PropTypes.func,
  showModifierScreen: PropTypes.func,
  onDelete: PropTypes.func
}

export default TotemRenderer
