import PropTypes from 'prop-types'
import {
  GET_MODIFIERS_ERROR,
  GET_MODIFIERS_SUCCESS,
  GET_MODIFIERS_SUCCESS_CLASSCODE,
  GET_MODIFIERS_ERROR_CLASSCODE
} from '../common/constants'

export default function modifiersReducer(state = null, action) {
  switch (action.type) {
  case GET_MODIFIERS_SUCCESS:
    return {
      data: action.data,
      loadingData: false
    }
  case GET_MODIFIERS_ERROR:
    return {
      data: action.error,
      loadingData: false
    }
  case GET_MODIFIERS_SUCCESS_CLASSCODE:
    return {
      data: action.data,
      priceChanged: null,
      classCode: action.classCode,
      loadingData: false
    }
  case GET_MODIFIERS_ERROR_CLASSCODE:
    return {
      data: action.error,
      loadingData: false
    }
  default:
    return state
  }
}

const ModifierGroupPropType = PropTypes.shape({
  partCode: PropTypes.number,
  name: PropTypes.string,
  price: PropTypes.number
})

export const ModifierClassPropType = PropTypes.shape({
  name: PropTypes.string,
  classCode: PropTypes.number,
  modifiersClass: PropTypes.arrayOf(ModifierGroupPropType)
})

