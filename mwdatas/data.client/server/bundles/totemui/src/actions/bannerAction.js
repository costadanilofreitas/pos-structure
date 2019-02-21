import axios from 'axios'
import { GET_BANNER_MAINSCREEN, GET_BANNER_TOPSCREEN, REQUEST_URL } from '../common/constants'

export const getUrlBannerAction = () => {
    const request = axios.get(`${REQUEST_URL}banner/topScreen`).then((resp) => {
        return resp.data
    })

    return {
        type: GET_BANNER_TOPSCREEN,
        payload: request
    }
}
export const getMainScreenUrlBannerAction = (totem_id) => {
    const request = axios.get(`${REQUEST_URL}banner/mainScreen/${totem_id}`).then((resp) => {
        return resp.data
    })

    return {
        type: GET_BANNER_MAINSCREEN,
        payload: request
    }
}