export const SHOW_DIALOG = 'SHOW_DIALOG'

export default function (type) {
  return {
    type: SHOW_DIALOG,
    payload: type
  }
}
