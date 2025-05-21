import { SET_CONSOLIDATED_ITEMS } from '../constants/actionTypes'

export default function setConsolidatedItemsAction(showConsolidatedItems) {
  return {
    type: SET_CONSOLIDATED_ITEMS,
    payload: showConsolidatedItems
  }
}
