import { CPF_CHANGED } from '../common/constants'

export default (value) => {
	return {
		type: CPF_CHANGED,
		payload: value
	}
}