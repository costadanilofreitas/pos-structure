import shallowEqual from 'react-redux/lib/utils/shallowEqual'
import _ from 'lodash'

const hasOwn = Object.prototype.hasOwnProperty

/**
 * Helper function to be used on shouldComponentUpdate, given an array of property names (that maps
 * to objects) it will make a shallow comparisson on all object keys.
 * If any other property or state is changed, it will return true.
 *
 * @param currentProps object current properties
 * @param currentState object current state
 * @param nextProps object next properties
 * @param nextState object next state
 * @param deepComp array list of keys that requires deep comparison
 * @param customVal function custom validation when one of the deepComp keys values is different
 * @return boolean true if render needed, otherwise false
 */
export const compareProps = (currentProps, currentState, nextProps, nextState, deepComp, customVal) => {
  if (!shallowEqual(currentState, nextState)) {
    return true
  }
  if (shallowEqual(currentProps, nextProps)) {
    return false
  }
  const currentKeys = _.keys(currentProps)
  const nextKeys = _.keys(nextProps)

  if (currentKeys.length !== nextKeys.length) {
    return false
  }

  for (let i = 0, len = currentKeys.length; i < len; i++) {
    const key = currentKeys[i]
    const doDeepComp = _.includes(deepComp, key)
    if (
      !hasOwn.call(nextProps, key) || ( // key missing in nextProps
        (currentProps[key] !== nextProps[key]) && ( // key different
          !doDeepComp || // doesn't require deep comparison
          !_.isEqual(currentProps[key], nextProps[key]) // is different
        )
      )
    ) {
      if (customVal && doDeepComp) {
        if (customVal(key, currentProps[key], nextProps[key])) {
          return true
        }
      } else {
        return true
      }
    }
  }
  return false
}

/**
 * Convert given value to boolean
 *
 * @param value string value to convert
 * @param def boolean default value in case that given value cannot be mapped to true or
 *                    false (e.g. undefined)
 * @return boolean value converted to boolean
 */
export const toBoolean = (value, def) => {
  const lowerVal = _.toLower(`${value}`)
  const isTrue = _.includes(['on', 'yes', 'true', 'y', 't', '1'], lowerVal)
  const isFalse = _.includes(['off', 'no', 'false', 'n', 'f', '0'], lowerVal)

  if (!isTrue && !isFalse) {
    return def || false
  }
  return isTrue
}

/**
 * Get translated message as a string, properly interpolated
 */
export const getMessage = (messages, formattedMessage) => {
  const props = (formattedMessage || {}).props || {}
  let id = props.id || ''
  const values = { ...(props.defaultValues || {}), ...(props.values || {}) }
  if (id.startsWith('$') && _.includes(id, '|')) {
    const idSplitted = id.split('|')
    id = idSplitted[0]
    _.forEach(idSplitted.slice(1), (item, idx) => {
      values[idx] = item
    })
  }
  const translation = messages[id] || props.defaultMessage
  if (!_.isEmpty(values)) {
    // needs interpolation
    const splitted = translation.split(/(?:{|%{)(.*?)(?:})/gm)
    const interpolated = []
    splitted.forEach((str, idx) => {
      if ((idx % 2) === 0) {
        interpolated.push(str)
      } else {
        const child = values[str]
        if (typeof child === 'string') {
          interpolated.push(child)
        } else {
          interpolated.push(getMessage(messages, child))
        }
      }
    })
    return interpolated.join('')
  }
  return translation
}

export const ignoreGlobalTimer = {
  areStatesEqual: (next, prev) => next.globalTimer !== prev.globalTimer
}
