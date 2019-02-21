import {
	POST_SALE_START, TYPE_CHANGED, CPF_CHANGED, COUPON_CHANGED, NAME_CHANGED,
	CLEAN_UP_STATES, DO_SALE, POST_SALE_ADDITEM, POST_SALE_REMOVEITEM,
	POST_SALE_ADDPAYMENT, GET_CUPOM, POST_SALE_CHANGEITEM, APAGAR_CHANGED,
	GET_SALE_CHECKPAYMENT, EXPANDED_FOOTER
} from "../common/constants"
import _ from 'lodash'

const INITIAL_STATE = {
	items: [],
	cpf: '',
	sale_token: '',
	type: '',
	clientName: '',
	couponCode: '',
	coupon: '',
	aPagar: null,
	expandedFooter: false
}

export default (state = INITIAL_STATE, action) => {
	switch (action.type) {
		case POST_SALE_START:
			return { ...state, sale_token: action.payload.data }
		case GET_CUPOM:
			return { ...state, coupon: action.payload }
		case TYPE_CHANGED:
			return { ...state, type: action.payload }
		case CPF_CHANGED:
			return { ...state, cpf: action.payload }
		case COUPON_CHANGED:
			return { ...state, couponCode: action.payload }
		case NAME_CHANGED:
			return { ...state, clientName: action.payload }
		case APAGAR_CHANGED:
			return { ...state, aPagar: action.payload }
		case POST_SALE_ADDITEM:
			let items = [...state.items, action.payload]
			return { ...state, items }
		case GET_SALE_CHECKPAYMENT:
			switch (action.payload.data[0]) {
				case 201:
					return { ...state, aPagar: action.payload.data[1] }
				case 200:
					return { ...state, aPagar: 0 }
			}
			return state

		case POST_SALE_CHANGEITEM:
			{
				const lineNumber = action.payload.line
				const items = [..._.filter(state.items, (item) => item.line != lineNumber), action.payload]
				return { ...state, items: _.sortBy(items, 'line') }
			}
		case POST_SALE_REMOVEITEM:
			{
				const lineToRemove = action.payload
				const newItems = _.filter(state.items, (item) => item.line != action.payload)
				return { ...state, items: newItems }
			}
		case EXPANDED_FOOTER:
			return { ...state, expandedFooter: action.payload }
		case CLEAN_UP_STATES:
			return INITIAL_STATE
		// return { ...state, type: null, items: [], clientName: "", sale_token: '', payment_token: '' }
	}
	return state
}