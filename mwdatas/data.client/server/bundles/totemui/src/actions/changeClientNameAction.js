import { NAME_CHANGED } from '../common/constants'

export default (value) => {
	return {
		type: NAME_CHANGED,
		payload: value
	}
}