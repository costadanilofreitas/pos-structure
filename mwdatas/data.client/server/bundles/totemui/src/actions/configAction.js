import axios from 'axios'
import { ALTER_TIME_COUNTER, CONFIG, OPTION_LABELS, REQUEST_URL } from '../common/constants'


export const getOptionsLabelAction = () => {
    const request = axios.get(`${REQUEST_URL}option/labels`)
    return {
        type: OPTION_LABELS,
        payload: request
    }
}

export const configAction = () => {
    const request = axios.get(`${REQUEST_URL}config`).then((data) => {
        return data.data
    }).catch((errorResponse) => {
        return errorResponse
    })
    return {
        type: CONFIG,
        payload: request
    }
}

export const alterTimeCounterAction = (num) => {
    return {
        type: ALTER_TIME_COUNTER,
        payload: num
    }
}
