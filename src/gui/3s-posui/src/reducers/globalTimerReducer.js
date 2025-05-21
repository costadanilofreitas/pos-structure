import { GLOBAL_TIMER_TICK } from '../constants/actionTypes'

const DEFAULT_TICK = 0

export default function (state = DEFAULT_TICK, action = {}) {
  if (action.type === GLOBAL_TIMER_TICK) {
    return Math.floor(action.payload / 1000)
  }
  return state
}
