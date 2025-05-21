import { BUTTON_DOWN } from '../constants/actionTypes'

export default function buttonDownAction(text) {
  return {
    type: BUTTON_DOWN,
    payload: { text }
  }
}
