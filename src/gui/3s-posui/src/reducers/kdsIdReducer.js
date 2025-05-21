import queryString from 'query-string'

const qs = queryString.parse(location.search)
const DEFAULT_KDS_ID = parseInt(qs.kdsid, 10)

export default function (state = DEFAULT_KDS_ID) {
  return state
}
