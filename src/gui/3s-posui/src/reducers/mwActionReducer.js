import _ from 'lodash'
import {
  EXECUTE_ACTION_REQUESTED, EXECUTE_ACTION_SUCCEEDED, EXECUTE_ACTION_FINISHED,
  EXECUTE_ACTION_FAILED, EXECUTE_ACTION_PROCESSED, RESYNC
} from '../constants/actionTypes'

const DEFAULT_ACTION_STATE = {}

const setBusyFlag = (state, set) => {
  if (set) {
    return {
      ...state,
      busy: true
    }
  }
  // check if we can remove the flag
  const remainingKeys = _.keys(state)
  if (remainingKeys.length === 1 && remainingKeys[0] === 'busy') {
    // last action in progress was removed, remove busy flag
    return _.omit(state, 'busy')
  }
  return state
}

/**
 * An object representing current asynchronous actions in progress, indexed by local
 * action id, generated on the client side.
 *
 * Example:
 * {
 *   'busy': true,
 *   'action_123': {
 *     inProgress: true,  // set to false when response is received
 *     actionId: '88',  // server-assigned action id
 *     data: null  // will contain the response data
 *   }
 * }
 *
 * Notice that busy flag will be present only when there is at least one action in progress.
 * If there is no action in progress, the state will be an empty object.
 */
export default function (state = DEFAULT_ACTION_STATE, action = null) {
  const payload = action.payload || {}
  switch (action.type) {
    case EXECUTE_ACTION_REQUESTED:
      return setBusyFlag(state, true)
    case EXECUTE_ACTION_SUCCEEDED:
      if (payload.ok) {
        // action was successfully started on the server
        if (!payload.uid) {
          // executer does not want to track the response
          return state
        }
        return {
          ...state,
          [payload.uid]: {
            inProgress: true,
            actionId: String(payload.data),
            data: null
          }
        }
      }
      // something went wrong, remove the action flag if necessary
      return setBusyFlag(state, false)
    case EXECUTE_ACTION_FINISHED: {
      // store the response and set inProgress to false
      const localActionId = _.findKey(state, ['actionId', String(payload.actionId)])
      if (!localActionId) {
        // response was not tracked
        return setBusyFlag(state, false)
      }
      return {
        ...state,
        [localActionId]: {
          inProgress: false,
          actionId: String(payload.actionId),
          data: payload.data
        }
      }
    }
    case EXECUTE_ACTION_FAILED:
      return setBusyFlag(state, false)
    case EXECUTE_ACTION_PROCESSED:
      return setBusyFlag(_.omit(state, payload.uid), false)
    case RESYNC:
      return DEFAULT_ACTION_STATE
    default:
  }

  return state
}
