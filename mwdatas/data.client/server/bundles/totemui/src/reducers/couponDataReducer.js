import { GET_CUPOM_PRODUCTS } from "../common/constants"

export default (state = [], action) => {

    switch (action.type) {
        case GET_CUPOM_PRODUCTS:
            return action.payload
    }
    return state
}