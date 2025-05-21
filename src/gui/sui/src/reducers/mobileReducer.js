import queryString from 'query-string'

const qs = queryString.parse(location.search)
const MOBILE = qs.mobile === 'true'

export default function (state = MOBILE) {
  return state
}
