export function getFormattedCurrencyDate(date) {
  const todayTime = date
  let month = todayTime.getMonth() + 1
  let day = todayTime.getDate()
  const year = todayTime.getFullYear()

  if (parseInt(day, 10) < 10) {
    day = `0${day}`
  }
  if (parseInt(month, 10) < 10) {
    month = `0${month}`
  }
  return `${day}/${month}/${year}`
}

export function getFormattedDateWithYYYYmmDD(date) {
  const day = date.substring(6, 8)
  const month = date.substring(4, 6)
  const year = date.substring(0, 4)
  return `${day}/${month}/${year}`
}

export function getBusinessDate(dateString) {
  const day = parseInt(dateString.substring(6, 8), 10)
  const month = parseInt(dateString.substring(4, 6), 10) - 1
  const year = parseInt(dateString.substring(0, 4), 10)
  return new Date(year, month, day)
}
