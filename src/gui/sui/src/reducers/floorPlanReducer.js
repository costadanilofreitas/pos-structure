import { RESYNC } from '3s-posui/constants/actionTypes'
import { FLOOR_PLAN_CHANGED, FLOOR_PLAN_LOADED } from '../constants/actionTypes'


export default function floorPlanReducer(state, action) {
  if (action && action.type && action.type === RESYNC) {
    return null
  }

  if (action && action.type && action.type === FLOOR_PLAN_CHANGED) {
    if (action.payload != null) {
      return {
        ...state,
        active: action.payload
      }
    }
  }

  if (action && action.type && action.type === FLOOR_PLAN_LOADED) {
    if (action.payload != null) {
      return {
        ...state,
        enabled: (action.payload.enabled || 'false').toLowerCase() === 'true',
        height: parseInt(action.payload.height || '1024', 10),
        width: parseInt(action.payload.width || '768', 10),
        rotation: parseInt(action.payload.rotation || '0', 10),
        plan: action.payload.plan
      }
    }
  }

  if (state != null) {
    return state
  }

  return {
    active: true,
    enabled: false,
    height: 0,
    width: 0,
    rotation: 0,
    plan: {}
  }
}
