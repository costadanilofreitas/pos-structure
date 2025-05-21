export function isEsc(event) {
  return event.keyCode === 27
}

export function isEnter(event) {
  return event.keyCode === 13
}

export function isTab(event) {
  return event.keyCode === 9
}

export function isKeyUp(event) {
  return event.keyCode === 40
}

export function isKeyDown(event) {
  return event.keyCode === 38
}

export function includesMask(value) {
  return ['9', 'a', '*'].includes(value)
}
