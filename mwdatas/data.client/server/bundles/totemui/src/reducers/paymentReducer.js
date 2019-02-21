import { PAYMENT_CHANGED, CLEAN_UP_STATES } from "../common/constants"

export default (state = {}, action) => {
	switch (action.type) {
	case PAYMENT_CHANGED:
		return {
			...state, 
			type: action.payload
		}
	case CLEAN_UP_STATES:
		return {
			...state,
			type: null
		}
	}
	return state
}