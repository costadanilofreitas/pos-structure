import { ERROR } from "../common/constants"

const INITIAL_STATE = {
    code: 0,
    menssageCode: '',
    type: '',
}

export default (state = INITIAL_STATE, action) => {
    switch (action.type) {
        case ERROR:
            let code = ''
            let menssageCode = ''
            let type = action.payload.type
            if (action.payload.payload) {
                code = action.payload.payload.response ? action.payload.payload.response.status : ''
                menssageCode = `${action.payload.payload.message || ''} : ${JSON.stringify((((action.payload || {}).payload || {}).response || {}).data || '') || ''}`
            } else {
                code = action.payload.response ? action.payload.response.status : ''
                menssageCode = action.payload.message ? action.payload.message : ''
            }

            return { ...state, code, menssageCode, type }
    }
    return state
}