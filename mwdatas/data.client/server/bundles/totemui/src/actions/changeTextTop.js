import { TITLE_CHANGED } from '../common/constants'

export default (value) => {
	return {
		type: TITLE_CHANGED,
		payload: value
	}
}