import { UPDATING_WINDOW_SIZE } from '../constants/actionTypes'

export default (width, height) => {
  return {
    type: UPDATING_WINDOW_SIZE, width, height
  }
}
