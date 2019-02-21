import { ACUMULATE_CHANGED } from "../common/constants"

export default (state = {}, action) => {

    switch (action.type) {
        case ACUMULATE_CHANGED:
            return action.payload
    }
    return state
}