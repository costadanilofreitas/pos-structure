import { TOUCH_COMMAND } from '../constants/actionTypes'

export default function sendTouchCommandAction(command) {
  return {
    type: TOUCH_COMMAND,
    payload: command
  }
}
