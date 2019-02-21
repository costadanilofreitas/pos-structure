import { TITLE_CHANGED, CLEAN_UP_STATES, TEXT_TOP_MAIN } from "../common/constants"

export default (state = '', action) => {
    switch (action.type) {
    case TITLE_CHANGED:
        return action.payload
    case CLEAN_UP_STATES:
    	return ''
    }
    return state
}