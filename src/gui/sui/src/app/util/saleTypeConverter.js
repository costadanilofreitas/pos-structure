import _ from 'lodash'
import SaleType from '../model/SaleType'


export function getJoinedAvailableSaleTypes(availableSaleTypes) {
  const saleTypes = []
  _.forEach(availableSaleTypes, (saleType) => {
    if (saleType.length > 1) {
      _.forEach(saleType, (joinedSaleTypes) => {
        if (!saleTypes.includes(joinedSaleTypes)) {
          saleTypes.push(joinedSaleTypes)
        }
      })
    } else if (!saleTypes.includes(saleType[0])) {
      saleTypes.push(saleType[0])
    }
  })
  return saleTypes
}


export function getShortedSaleTypes(joinedSaleTypes) {
  const shortedSaleTypes = []
  _.forEach(joinedSaleTypes, (saleType) => {
    if (Object.keys(SaleType).includes(saleType)) {
      shortedSaleTypes.push(SaleType[saleType])
    }
  })
  return shortedSaleTypes
}
