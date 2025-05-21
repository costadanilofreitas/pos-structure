import { SET_PAGINATION_BLOCK_SIZE } from '../constants/actionTypes'

const DEFAULT_PAGINATION_BLOCK_SIZE = 0

export default function (state = DEFAULT_PAGINATION_BLOCK_SIZE, action = null) {
  if (action.type === SET_PAGINATION_BLOCK_SIZE) {
    return action.payload
  }

  return state
}
