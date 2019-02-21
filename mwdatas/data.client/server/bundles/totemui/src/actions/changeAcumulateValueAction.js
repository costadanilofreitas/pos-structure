import { ACUMULATE_CHANGED } from '../common/constants'

export default (value) => {
    return {
        type: ACUMULATE_CHANGED,
        payload: value
    }
}