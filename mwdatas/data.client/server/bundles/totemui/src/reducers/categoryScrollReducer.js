import { SET_SCROLL, CLEAN_UP_STATES } from "../common/constants"

export default (state = 0, action) => {
    switch (action.type) {
        case SET_SCROLL:
            return action.payload
        case CLEAN_UP_STATES:
            return 0
    }
    return state
}