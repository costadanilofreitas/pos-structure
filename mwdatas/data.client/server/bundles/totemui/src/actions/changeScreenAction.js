import { CHANGE_SCREEN } from '../common/constants'

export default (screen) => {
	return {
		type: CHANGE_SCREEN,
		payload: screen
	}
}