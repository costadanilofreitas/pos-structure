import { SET_KDS_VIEW } from '../constants/actionTypes'

export default (view) => {
  return {
    type: SET_KDS_VIEW,
    payload: view
  }
}
