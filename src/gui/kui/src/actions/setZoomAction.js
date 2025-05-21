import { SET_KDS_ZOOM } from '../constants/actionTypes'

export default (view) => {
  return {
    type: SET_KDS_ZOOM,
    payload: view
  }
}
