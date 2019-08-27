import Cookies from 'universal-cookie'
import axios from 'axios/index'

import config from '../config'

export const LOGIN_USER = 'LOG_USER'
export const LOGOUT_USER = 'LOGOUT_USER'

const cookies = new Cookies()

export function loginUser(user) {
  return {
    type: LOGIN_USER,
    user: user
  }
}

export function logoutUser(token) {
  cookies.remove('tokenUser')

  axios({
    method: 'post',
    url: config.apiBaseUrl + '/logout/',
    headers: { 'Auth-Token': token }
  })

  return {
    type: LOGOUT_USER
  }
}
