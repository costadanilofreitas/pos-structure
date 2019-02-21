import axios from 'axios'
import {
    GET_PRODUCT_INCATEGORY, GET_PRODUCT_SALEOPTIONS, REQUEST_URL, CLEAN_SALEOPTIONS,
    DO_SALE, ALTER_URL_TOP, OPTION_LABELS, ALTER_PRODUCT, SHOW_SUGGESTION, SET_PRODUCT_SUGGESTION,
    EXPANDED_FOOTER
} from '../common/constants'


export const setListProductAction = (list) => {
    return {
        type: GET_PRODUCT_INCATEGORY,
        payload: list
    }
}

export const productInCategoryAction = (id) => {
    const request = axios.get(`${REQUEST_URL}product/inCategory/` + id).then(
        (data) => { return data.data }
    )
    return {
        type: GET_PRODUCT_INCATEGORY,
        payload: request
    }
}

export const productSaleOptionsAction = (productCode, context=null) => {
    const request = axios.get(`${REQUEST_URL}product/${productCode}/saleOptions${context ? `/${context}` : ''}`)
    return {
        type: GET_PRODUCT_SALEOPTIONS,
        payload: request
    }
}

export const cleanSaleOptions = () => {
    return {
        type: CLEAN_SALEOPTIONS
    }
}

export const alterProductAction = (product) => {
    return {
        type: ALTER_PRODUCT,
        payload: product
    }
}

export const registerProductAction = (partCode, currentyQuantity, isSuggestion, size) => {
    const request = axios.get(`${REQUEST_URL}product/` + partCode)
        .then((response) => {
            response.data.isSuggestion = isSuggestion
            if (currentyQuantity) {
                response.data.currentQuantity = currentyQuantity
            }
            response.data.size = size

            return response.data
        })

    return {
        type: DO_SALE,
        payload: request
    }
}

export const SetProductFromSuggestionAction = (list) => {
    return {
        type: SET_PRODUCT_SUGGESTION,
        payload: list
    }
}


export const changeProductAction = (product) => {
    return {
        type: DO_SALE,
        payload: product
    }
}

export const alterUrlTopAction = (url) => {
    return {
        type: ALTER_URL_TOP,
        payload: url
    }
}

export const showSuggestionAction = (show) => {
    return {
        type: SHOW_SUGGESTION,
        payload: show
    }
}

export const expandedFooterAction = (expanded) => {
    return {
        type: EXPANDED_FOOTER,
        payload: expanded
    }
}