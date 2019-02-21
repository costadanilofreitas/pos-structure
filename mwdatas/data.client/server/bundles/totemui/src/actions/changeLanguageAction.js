import { LANGUAGE_CHANGED } from '../common/constants'

export default (value) => {
	return {
		type: LANGUAGE_CHANGED,
		payload: value
	}
}