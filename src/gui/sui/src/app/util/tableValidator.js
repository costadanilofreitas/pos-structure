export function tableNotInState(table, ...status) {
  const notValid = table == null || table.status == null
  return notValid ? true : status.every(state => {
    return table.status !== state
  })
}

export function tableInState(table, ...status) {
  const notValid = table == null || table.status == null
  return notValid ? false : status.some(state => {
    return table.status === state
  })
}
