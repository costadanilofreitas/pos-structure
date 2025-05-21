export function operatorIsNotInState(operator, ...states) {
  const notValid = operator == null || operator.state == null
  return notValid ? true : states.every(state => {
    return operator.state !== state
  })
}

export function operatorIsInState(operator, ...states) {
  const notValid = operator == null || operator.state == null
  return notValid ? false : states.some(state => {
    return operator.state === state
  })
}
