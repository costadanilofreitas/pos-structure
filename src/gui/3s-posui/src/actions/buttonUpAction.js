import { BUTTON_UP } from '../constants/actionTypes'

export default function buttonUpAction(text, clicked) {
  return {
    type: BUTTON_UP,
    payload: { text, clicked }
  }
}
