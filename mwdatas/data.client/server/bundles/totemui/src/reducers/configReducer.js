import { ALTER_TIME_COUNTER, CONFIG, OPTION_LABELS } from "../common/constants"

const INITIAL_STATE = {
    time: null,
    timeCounter: 40,
    optionLabels: [],
}

export default (state = INITIAL_STATE, action) => {
    switch (action.type) {
        case CONFIG:
            return { ...state, time: action.payload.time }
        case OPTION_LABELS:
            return { ...state, optionLabels: action.payload }
        case ALTER_TIME_COUNTER:
            return { ...state, timeCounter: action.payload }
    }

    return state
}