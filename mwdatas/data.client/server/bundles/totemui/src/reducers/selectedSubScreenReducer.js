import { SUB_SCREEN_CHANGED, CLEAN_UP_STATES } from "../common/constants"

export default (state = null, action) => {
	switch (action.type) {
	case SUB_SCREEN_CHANGED:
		return action.payload
	case CLEAN_UP_STATES:
		return null
	}
	return state
}