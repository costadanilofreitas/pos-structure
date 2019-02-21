import axios from 'axios'
import { GET_CATEGORY_ALL, MENU_CATEGORY_CHANGED, REQUEST_URL } from '../common/constants'

export const categoryAllAction = () => {
    const request = axios.get(`${REQUEST_URL}category/all`)
    return {
        type: GET_CATEGORY_ALL,
        payload: request
    }
}

export const selectMenuCategoryAction = (id) => {
    return {
        type: MENU_CATEGORY_CHANGED,
        payload: id
    }
}