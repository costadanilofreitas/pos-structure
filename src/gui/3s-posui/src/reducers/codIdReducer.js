import queryString from 'query-string'

const qs = queryString.parse(location.search)
const DEFAULT_COD_ID = parseInt(qs.codid, 10)

export default function (state = DEFAULT_COD_ID) {
  return state
}
