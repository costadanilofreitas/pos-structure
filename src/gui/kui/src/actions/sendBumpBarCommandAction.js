import { KDS_COMMAND } from '../constants/actionTypes'

export default function sendBumpBarCommandAction(command) {
  return {
    type: KDS_COMMAND,
    payload: { '@attributes': { name: command.command, orderId: command.orderId } }
  }
}
