import { COUPON_CHANGED } from '../common/constants'

export default (value) => {
	return {
		type: COUPON_CHANGED,
		payload: value
	}
}