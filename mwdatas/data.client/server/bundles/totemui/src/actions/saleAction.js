import axios from 'axios'
import { Dispatch } from 'redux'
import { CONFIG, ERROR, POST_SALE_START, POST_SALE_ADDITEM, POST_SALE_ADDPAYMENT, GET_SALE_CHECKPAYMENT, GET_SALE_SUGGESTEDPRODUCTS, GET_CUPOM, POST_SALE_ADDCUSTOMERINFO, TYPE_CHANGED, REQUEST_URL, POST_SALE_REMOVEITEM, POST_SALE_CHANGEITEM, APAGAR_CHANGED, CLEAN_UP_STATES } from '../common/constants'
import _ from 'lodash'

export const saleStartAction = (totem_id, culture, sale_type) => {
    const request = axios.post(`${REQUEST_URL}sale/start/${totem_id}/${culture}/${sale_type}`).catch((errorResponse) => {
        return errorResponse
    })

    return {
        type: POST_SALE_START,
        payload: request
    }
}

export const saleCancelAction = (sale_token) => {
    const request = axios.post(`${REQUEST_URL}sale/${sale_token}/cancel`).catch((errorResponse) => {
        return errorResponse
    })

    return {
        type: CLEAN_UP_STATES
    }
}

export const saleAddItemAction = (sale_token, data) => {
    const lineNumber = data.line
    if (lineNumber) {
        return {
            type: POST_SALE_CHANGEITEM,
            payload: axios.post(`${REQUEST_URL}sale/${sale_token}/changeItem/${lineNumber}`, JSON.stringify(data))
                .then(() => data)
                .catch((errorResponse) => {
                    return errorResponse
                })
        }
    } else {
        const request = axios.post(`${REQUEST_URL}sale/${sale_token}/addItem`, JSON.stringify(data))
            .then((result) => {
                const newData = _.cloneDeep(data)
                newData.line = result.data
                return newData
            }).catch((errorResponse) => {
                return errorResponse
            })

        return {
            type: POST_SALE_ADDITEM,
            payload: request
        }
    }
}

export const saleRemoveItemAction = (sale_token, line_number) => {
    const request = axios.post(`${REQUEST_URL}sale/${sale_token}/removeItem/${line_number}`).then((result) => {
        return line_number
    })

    return {
        type: POST_SALE_REMOVEITEM,
        payload: request
    }
}

export const saleAddPaymentAction = (sale_token, data) => {
    const request = axios.post(`${REQUEST_URL}sale/${sale_token}/addPayment`, JSON.stringify(data))
    return {
        type: POST_SALE_ADDPAYMENT,
        payload: request
    }
}

export const saleCheckPaymentAction = (sale_token, body) => {
    const request = axios.post(`${REQUEST_URL}sale/${sale_token}/checkPayment/1`, body).catch((errorResponse) => {
        return errorResponse
    })
    return {
        type: GET_SALE_CHECKPAYMENT,
        payload: request
    }
}

export const saleSuggestedProductsAction = (sale_token, category = null) => {
    const request = axios.get(`${REQUEST_URL}sale/${sale_token}/suggestedProducts/${category}`)
    return {
        type: GET_SALE_SUGGESTEDPRODUCTS,
        payload: request
    }
}

export const saleAddCustomerInfoAction = (sale_token, data) => {
    const request = axios.post(`${REQUEST_URL}sale/${sale_token}/addCustomerInfo`, JSON.stringify(data))

    return {
        type: POST_SALE_ADDCUSTOMERINFO,
        payload: request
    }
}

export const typeChangedAction = (sale_type) => {
    return {
        type: TYPE_CHANGED,
        payload: sale_type
    }
}

export const cupomAction = (cupom_code) => {
    const request = axios.get(`${REQUEST_URL}cupom/${cupom_code}`).then((data) => {
        return data.data
    })
    return {
        type: GET_CUPOM,
        payload: request
    }
}


export const saleApagarChangedAction = (value) => {
    return {
        type: APAGAR_CHANGED,
        payload: value
    }
}