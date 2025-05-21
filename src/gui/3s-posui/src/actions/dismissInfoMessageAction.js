import { DISMISS_INFO_MESSAGE } from '../constants/actionTypes'

export default function dismissInfoMessageAction() {
  return {
    type: DISMISS_INFO_MESSAGE,
    payload: null
  }
}
