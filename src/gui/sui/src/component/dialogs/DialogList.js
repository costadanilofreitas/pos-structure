import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { I18N, MessageBus } from '3s-posui/core'

import FilterableListBox from './filterable-list-box-dialog'
import KeyboardDialog from './keyboard-dialog'
import MessageOptionsDialog from './message-options-dialog'
import MessageDialog from './message-dialog'
import NumPadDialog from './numpad-dialog'
import DailyGoals from './daily-goals'
import PrintPreviewDialog from './print-preview-dialog'
import TimeoutDialog from './timeout-dialog'
import OrderPreviewDialog from './order-preview-dialog'
import TextPreviewDialog from './text-preview-dialog'
import BordereauDialog from './bordereau-dialog'
import RuptureDialog from './rupture-dialog'
import DeliveryAddressDialog from './delivery-address-dialog'


const dialogsList = {
  filteredListBox: FilterableListBox,
  keyboard: KeyboardDialog,
  messagebox: MessageOptionsDialog,
  messageDialog: MessageDialog,
  messageOptionsDialog: MessageOptionsDialog,
  numpad: NumPadDialog,
  numpad_password: NumPadDialog,
  numpadDialog: NumPadDialog,
  dailyGoals: DailyGoals,
  printpreview: PrintPreviewDialog,
  timeout: TimeoutDialog,
  orderpreview: OrderPreviewDialog,
  listbox: FilterableListBox,
  textpreview: TextPreviewDialog,
  bordereauDialog: BordereauDialog,
  custom: KeyboardDialog,
  nopad: KeyboardDialog,
  rupture: RuptureDialog,
  deliveryAddress: DeliveryAddressDialog
}

class DialogList extends PureComponent {
  constructor(props) {
    super(props)
    this.messageBus = new MessageBus(this.props.posId)
  }

  closeDialog(dialogId, button, value) {
    let valueString = button
    if (value !== null && value !== undefined) {
      valueString += `,${value}`
    }

    this.messageBus.sendDialogResponseMessage(dialogId, valueString).then(() => null)
  }

  renderDialogs() {
    const { dialogs, excludeTypes, customDialogs, flatStyle } = this.props
    const sortedDialogs = [...dialogs]
    sortedDialogs.sort((l, r) => l.id - r.id)
    return sortedDialogs.map(dlg => {
      const overrideProps = {}
      let componentClass = null
      let message = dlg.message
      const customDialog = customDialogs[dlg.type] || null
      if (!_.includes(excludeTypes, dlg.type)) {
        if (customDialog !== null) {
          componentClass = customDialog
        }
      }

      if (componentClass === null) {
        const dialog = _.find(dialogs, ['id', dlg.id])
        console.error(`Invalid dialog type ${dlg.type} POS: ${this.props.posId} Dialog:`, dialog)
        componentClass = MessageDialog
        overrideProps.btn = ['$OK']
        overrideProps.title = 'DialogList'
        overrideProps.info = ''
        overrideProps.icon = 'error'
        message = `Invalid dialog type ${dlg.type}`
      }

      return (
        React.createElement(
          componentClass,
          {
            key: dlg.id,
            closeDialog: (button, value) => this.closeDialog(dlg.id, button, value),
            ...this.props,
            ...dlg,
            ...overrideProps,
            flatStyle: flatStyle,
            nopad: dlg.type === 'nopad'
          },
          <I18N id={message} />
        )
      )
    })
  }

  render() {
    return (
      <div>
        {this.renderDialogs()}
      </div>
    )
  }
}

DialogList.propTypes = {
  flatStyle: PropTypes.bool,
  excludeTypes: PropTypes.array,
  dialogs: PropTypes.array,
  posId: PropTypes.number,
  customDialogs: PropTypes.object
}

DialogList.defaultProps = {
  excludeTypes: [],
  customDialogs: dialogsList
}

function mapStateToProps(state) {
  return {
    dialogs: state.dialogs,
    posId: state.posId
  }
}

export default connect(mapStateToProps)(DialogList)
