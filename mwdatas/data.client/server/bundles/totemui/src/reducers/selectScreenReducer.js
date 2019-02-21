import { CHANGE_SCREEN, CLEAN_UP_STATES, START_SCREEN } from "../common/constants"

export default (state = null, action) => {
	switch (action.type) {
	case CHANGE_SCREEN:
		return action.payload
	case CLEAN_UP_STATES:
		return START_SCREEN
	}
	return state
}