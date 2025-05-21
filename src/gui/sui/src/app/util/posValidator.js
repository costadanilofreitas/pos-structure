export function posIsNotInState(posState, ...states) {
  const notValid = posState == null || posState.state == null
  return notValid ? true : states.every(state => {
    return posState.state !== state
  })
}

export function posIsInState(posState, ...states) {
  const notValid = posState == null || posState.state == null
  return notValid ? true : states.some(state => {
    return posState.state === state
  })
}
