import { LOGIN_USER, LOGOUT_USER } from '../actions/userActions'

export default function userReducer(state = null, action) {
  switch (action.type) {
  case LOGIN_USER:
    return action.user
  case LOGOUT_USER:
    return null
  default:
    return state
  }
}
