export const CHANGE_SALE_TYPE = 'CHANGE_SALE_TYPE'

// Reducers
export default function saleTypeReducer(state = null, action = null) {
  if (action.type === CHANGE_SALE_TYPE) {
    return action.saleType
  }
  return state
}

// Actions creators
export function changeSaleType(saleType) {
  return {
    type: CHANGE_SALE_TYPE,
    saleType
  }
}
