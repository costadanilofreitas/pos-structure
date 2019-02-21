import { GET_BANNER_TOPSCREEN } from "../common/constants"

const INITIAL_STATE = {
    urlBanner: ''
}


export default (state = INITIAL_STATE, action) => {
    switch (action.type) {
        case GET_BANNER_TOPSCREEN:
            return { ...state, urlBanner: action.payload }
    }
    return state
}