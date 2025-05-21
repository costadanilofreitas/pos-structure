import { INFO_MESSAGE_CHANGED } from '../constants/actionTypes'

export default function showInfoMessageAction(msg, timeout = '3000', type = 'info') {
  return {
    type: INFO_MESSAGE_CHANGED,
    payload: { msg, timeout, type }
  }
}
