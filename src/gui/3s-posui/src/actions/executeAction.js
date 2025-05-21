import { EXECUTE_ACTION, EXECUTE_ACTION_PROCESSED } from '../constants/actionTypes'


export function executeAction(uid, actionName, ...params) {
  return {
    type: EXECUTE_ACTION,
    payload: { uid, actionName, params }
  }
}


export function executeActionProcessed(uid) {
  return {
    type: EXECUTE_ACTION_PROCESSED,
    payload: { uid }
  }
}
