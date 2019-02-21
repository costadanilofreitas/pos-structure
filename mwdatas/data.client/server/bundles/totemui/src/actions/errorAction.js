import { ERROR } from '../common/constants'

export default function (error) {
	return {
		type: ERROR,
		payload: error
	}
}