import { SUB_SCREEN_CHANGED } from '../common/constants'

export default (id) => {
	return {
		type: SUB_SCREEN_CHANGED,
		payload: id
	}
}