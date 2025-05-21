import queryString from 'query-string'
import DeviceType from '../constants/Devices'

const qs = queryString.parse(location.search)
const TOTEM = qs.totem === 'true'
const MOBILE = qs.mobile === 'true'

export default function (state = null) {
  if (state != null) {
    return state
  }

  if (TOTEM) {
    return DeviceType.Totem
  } else if (MOBILE) {
    return DeviceType.Mobile
  }

  return DeviceType.Desktop
}
