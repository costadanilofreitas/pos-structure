import { MODAL_CHANGED, CLEAN_UP_STATES } from "../common/constants"

export default (state = null, action) => {
    switch (action.type) {
        case MODAL_CHANGED:
            return action.payload
        case CLEAN_UP_STATES:
        	return null
    }
    return state
}