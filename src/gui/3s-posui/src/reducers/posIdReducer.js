import queryString from 'query-string'

const qs = queryString.parse(location.search)
const DEFAULT_POS_ID = parseInt(qs.posid, 10)

export default function (state = DEFAULT_POS_ID) {
  return state
}
