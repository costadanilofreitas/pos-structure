import { LANGUAGE_CHANGED } from '../constants/actionTypes'

export default function setLanguageAction(langCode) {
  return {
    type: LANGUAGE_CHANGED,
    payload: {
      language: langCode
    }
  }
}
