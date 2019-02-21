import axios from 'axios'

import { REQUEST_URL, PRODUCTS, COMBOS, MODIFIERS, PRICE_MODIFIERS } from '../common/constants'

const request = (link, token) => axios.get(`${REQUEST_URL}${link}`, { 'headers': { 'Auth-Token': token } })
const requestProduct = (link, token, productCategory) => axios.get(`${REQUEST_URL}${link}/${productCategory}`, { 'headers': { 'Auth-Token': token } })

export function getAllData(dataRequest, token, productCategory = null) {
  switch (dataRequest) {
  case PRODUCTS:
    return requestProduct('priceList/products', token, productCategory)
  case COMBOS:
    return request('priceList/combos', token)
  case MODIFIERS:
    return request('modifiers/', token)
  case `${PRICE_MODIFIERS}${dataRequest.split('/')[2]}`:
    return request(dataRequest, token)
  default:
    return null
  }
}

export function saveProduct(dataRequest, product, newPrice, token) {
  switch (dataRequest) {
  case PRODUCTS:
    return axios({
      method: 'post',
      headers: { 'Auth-Token': token },
      url: `${REQUEST_URL}price/product/${product.partCode}`,
      data: newPrice
    })
  case COMBOS:
    return axios({
      method: 'post',
      headers: { 'Auth-Token': token },
      url: `${REQUEST_URL}price/combo/${product.comboPartCode}/${product.partCode}`,
      data: newPrice
    })
  case MODIFIERS:
    return axios({
      method: 'post',
      headers: { 'Auth-Token': token },
      url: `${REQUEST_URL}price/product/${product.optionPartCode}/${product.partCode}`,
      data: newPrice
    })
  default:
    return null

  }
}

export function saveModifier(product, newPrice, token, classCode) {
  return axios({
    method: 'post',
    headers: { 'Auth-Token': token },
    url: `${REQUEST_URL}price/modifier/${classCode}/${product.partCode}`,
    data: newPrice
  })
}

export function getToken(token) {
  return axios.get(`${REQUEST_URL}priceList/products`, { 'headers': { 'Auth-Token': token } })
}
