import { connect } from 'react-redux'
import React from 'react'

import { SHOW_DIALOG } from '../actions/showDialogAction'
import DialogType from '../constants/DialogType'

function mapDispatchToProps(dispatch) {
  return {
    showDialog: (payload) => {
      const seconds = new Date().getTime() / 1000
      const id = `local_dialog_${seconds}`
      let action = {
        type: 'DIALOGS_CHANGED',
        payload: [{
          id: id,
          timeout: payload.timeout || '60000',
          title: payload.title,
          message: payload.message,
          btn: ['$OK', '$CANCEL'],
          closeDialog: (dialogResponse) => {
            dispatch({
              type: 'DIALOG_CLOSED',
              payload: id
            })

            const button = dialogResponse.toString().split(',')[0]
            const value = dialogResponse.toString().split(',')[1]
            if (typeof payload.onClose === 'function') {
              if (button === '0') {
                if (payload.type === DialogType.Confirm) {
                  payload.onClose(true)
                } else if (payload.type === DialogType.NumberInput) {
                  if (payload.mask === 'NUMBER' || payload.mask === 'CURRENCY') {
                    payload.onClose(parseFloat(value))
                  } else {
                    payload.onClose(parseInt(value, 10))
                  }
                } else {
                  payload.onClose(value)
                }
              } else if (payload.type === DialogType.Confirm) {
                payload.onClose(false)
              } else {
                payload.onClose(null)
              }
            }
          }
        }]
      }

      if (payload.type === DialogType.List) {
        action.payload[0].type = 'listbox'
        action.payload[0].info = payload.list.join('|')
      } else if (payload.type === DialogType.NumberInput) {
        action.payload[0].type = 'numpad'
        action.payload[0].mask = payload.mask || 'INTEGER'
      } else if (payload.type === DialogType.Confirm || payload.type === DialogType.Alert) {
        action.payload[0].type = 'messagebox'
        action.payload[0].title = payload.title || '$CONFIRM'
        action.payload[0].message = payload.message
        action.payload[0].icon = payload.icon || 'info'
        action.payload[0].btn = payload.type === DialogType.Confirm ? ['$YES', '$NO'] : ['$OK']
      } else {
        action = {
          type: SHOW_DIALOG,
          payload: payload
        }
      }

      dispatch(action)
    }
  }
}

function withShowDialog(ComponentClass) {
  return connect(null, mapDispatchToProps)(
    function WithShowDialog(props) {
      return (<ComponentClass showDialog={props.showDialog} {...props}/>)
    })
}

export default withShowDialog
