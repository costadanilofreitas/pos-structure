import { MODAL_CHANGED } from '../common/constants'

export default (value) => {
    return {
        type: MODAL_CHANGED,
        payload: value
    }
}