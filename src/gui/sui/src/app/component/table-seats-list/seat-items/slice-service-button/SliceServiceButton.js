import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { I18N } from '3s-posui/core'
import ActionButton from '../../../../../component/action-button'
import { isOrderTakerFunction } from '../../../../model/modelHelper'
import TablePropTypes from '../../../../../prop-types/TablePropTypes'


export default class SliceServiceButton extends Component {
  constructor(props) {
    super(props)

    this.handleOnClose = this.handleOnClose.bind(this)
  }

  render() {
    const { workingMode, selectedTable } = this.props
    const disabled = isOrderTakerFunction(workingMode, selectedTable)

    return (
      <ActionButton
        className={'test_SliceServiceButton_SLICE'}
        executeAction={['do_slice_service', this.props.tableId, this.props.saleLines]}
        disabled={disabled}
        onActionFinish={(response) => this.handleOnClose(response)}
      >
        <i className="fas fa-cut fa" aria-hidden="true" style={{ margin: '0.5vh' }}/>
        <br/>
        <I18N id={'$SLICE_SERVICE'}/>
      </ActionButton>
    )
  }

  handleOnClose(response) {
    if (response) {
      this.props.setSeatScreen(false)
    }
  }
}

SliceServiceButton.propTypes = {
  tableId: PropTypes.string.isRequired,
  saleLines: PropTypes.string,
  setSeatScreen: PropTypes.func,
  workingMode: PropTypes.object,
  selectedTable: TablePropTypes
}
