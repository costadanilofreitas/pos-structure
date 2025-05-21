export const showAlert = (time, now, alert) => {
  return now > new Date(new Date(time).getTime() + (alert * 60000))
}

export const utcTimeNow = () => {
  return new Date(new Date().getTime() + (new Date().getTimezoneOffset() * 60000))
}
