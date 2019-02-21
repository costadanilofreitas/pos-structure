import { GET_CUPOM_PRODUCTS } from '../common/constants'

export default function(list) {
    return {
        type: GET_CUPOM_PRODUCTS,
        payload: list
    }
}