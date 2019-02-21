import { GET_CATEGORY_ALL } from "../common/constants"

const INITIAL_STATE = {
    allCategorys: []
}


export default (state = INITIAL_STATE, action) => {
    switch (action.type) {
        case GET_CATEGORY_ALL:
            let allCategorys = action.payload.data
            return { ...state, allCategorys }
    }
    return state
}