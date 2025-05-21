import { KDS_COMMAND } from '../constants/actionTypes'

export default function bumpAction() {
  return {
    type: KDS_COMMAND,
    payload: {
      '@attributes': {
        'name': 'bump'
      }
    }
  }
}
