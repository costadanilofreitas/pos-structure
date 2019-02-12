import { CHANGE_CURRENT_MENU } from '../constants/actionTypes'

export default function (menuId) {
  return {
    type: CHANGE_CURRENT_MENU,
    payload: menuId
  }
}
