import { I18N_FETCH_SUCCEEDED } from '../constants/actionTypes'

export default function (state = {}, action = null) {
  switch (action.type) {
    case I18N_FETCH_SUCCEEDED: {
      const l10n = {}
      // we need to put a $ sign in front of every translation
      const messages = action.payload.messages
      const keys = Object.keys(messages)
      for (let i = 0; i < keys.length; i++) {
        const oldKey = keys[i]
        if (oldKey.startsWith('L10N_')) {
          l10n[oldKey.slice(5)] = messages[oldKey]
        }
        const newKey = `$${oldKey}`
        Object.defineProperty(messages, newKey, Object.getOwnPropertyDescriptor(messages, oldKey))
        messages[newKey] = (messages[newKey] || '').replace(/\\/g, '{__break__}')
        delete messages[oldKey]
      }
      const formats = {
        number: {
          currency: {
            style: 'currency',
            currency: l10n.CURRENCY_CODE || 'USD', // ISO 4217
            minimumFractionDigits: parseInt(l10n.CURRENCY_DECIMALS || '2', 10)
          }
        }
      }

      return {
        ...state,
        language: action.payload.language.replace('_', '-'),
        messages,
        l10n,
        formats
      }
    }
    default:
  }

  return state
}
