import _ from 'lodash'
import {
    GET_PRODUCT_INCATEGORY, GET_PRODUCT_SALEOPTIONS, CLEAN_SALEOPTIONS,
    DO_SALE, ALTER_URL_TOP, OPTION_LABELS, ALTER_PRODUCT, GET_SALE_SUGGESTEDPRODUCTS,
    POST_SALE_ADDITEM, SHOW_SUGGESTION, CLEAN_UP_STATES, POST_SALE_CHANGEITEM
} from "../common/constants"

const INITIAL_STATE = {
    allProducts: [],
    allProductsSuggested: [],
    allOptions: [],
    modalSaleOptions: false,
    productCurrent: [],
    productCurrentImg: '',
    // productSale: [],
    error: false,
    showSuggestion: true,
    oldSuggestion: false
}




export default (state = INITIAL_STATE, action) => {
    switch (action.type) {
        case GET_PRODUCT_INCATEGORY:
            return { ...state, allProducts: action.payload }
        case GET_PRODUCT_SALEOPTIONS:
            let modalSaleOptions = action.payload.data.length > 1
            return { ...state, allOptions: action.payload, modalSaleOptions }
        case CLEAN_SALEOPTIONS:
            return { ...state, allOptions: [], modalSaleOptions: false }
        case DO_SALE:
            if (action.payload.isSuggestion) {
                return { ...state, productCurrent: [...state.productCurrent, action.payload], oldSuggestion: true }
            } else {
                return { ...state, productCurrent: [action.payload], oldSuggestion: false }
            }

        case POST_SALE_ADDITEM:
            let productCurrentAdd = []
            for (var index = 0; index < state.productCurrent.length; index++) {
                if (index > 0) {
                    productCurrentAdd.push(state.productCurrent[index])
                }
            }
            return { ...state, productCurrent: productCurrentAdd }
        case POST_SALE_CHANGEITEM:
            let productCurrentChange = []
            for (var index = 0; index < state.productCurrent.length; index++) {
                if (index > 0) {
                    productCurrentChange.push(state.productCurrent[index])
                }
            }
            return { ...state, productCurrent: productCurrentChange }
        case ALTER_PRODUCT:
            return { ...state, productCurrent: action.payload }
        case ALTER_URL_TOP:
            return { ...state, productCurrentImg: action.payload }
        case GET_SALE_SUGGESTEDPRODUCTS:
            return { ...state, allProductsSuggested: action.payload }
        case SHOW_SUGGESTION:
            return { ...state, showSuggestion: action.payload }
        case CLEAN_UP_STATES:
            return { ...INITIAL_STATE, allProducts: state.allOptions }
    }

    return state
}