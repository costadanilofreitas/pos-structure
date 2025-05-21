export default function parseISO8601Date(text, isGMT) {
  const regexp = '([0-9]{4})(-([0-9]{2})(-([0-9]{2})' +
                 '(T([0-9]{2}):([0-9]{2})(:([0-9]{2})(\\.([0-9]+))?)?' +
                 '(Z|(([-+])([0-9]{2}):([0-9]{2})))?)?)?)?'
  const d = text.match(new RegExp(regexp))
  if (!d) {
    return null
  }

  let offset = 0
  if (!d[1] || !d[3] || !d[5]) {
    return null
  }
  if (d[7] != null && (d[8] == null || d[10] == null)) {
    return null
  }

  const date = new Date(d[1], 0, 1)
  if (d[3]) {
    date.setMonth(d[3] - 1)
  }
  if (d[5]) {
    date.setDate(d[5])
  }
  if (d[7]) {
    date.setHours(d[7])
  }
  if (d[8]) {
    date.setMinutes(d[8])
  }
  if (d[10]) {
    date.setSeconds(d[10])
  }
  if (d[12]) {
    date.setMilliseconds(Number(`0.${d[12]}`) * 1000)
  }
  if (d[14]) {
    offset = (Number(d[16]) * 60) + Number(d[17])
    offset *= ((d[15] === '-') ? 1 : -1)
  }
  if (isGMT || d[13] === 'Z') {
    offset -= date.getTimezoneOffset()
  }
  const time = (Number(date) + (offset * 60 * 1000))
  date.setTime(Number(time))

  return date
}
