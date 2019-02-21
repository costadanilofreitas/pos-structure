import { SET_SCROLL } from '../common/constants'

export default function (amount = 0) {
    return {
        type: SET_SCROLL,
        payload: amount
    }
}