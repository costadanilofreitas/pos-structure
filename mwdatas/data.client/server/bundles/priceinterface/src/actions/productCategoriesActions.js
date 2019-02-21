export const GET_PRODUCT_CATEGORIES = 'GET_PRODUCT_CATEGORIES'

export function setProductCategories(categoriesList) {
  return {
    type: GET_PRODUCT_CATEGORIES,
    categoriesList: categoriesList
  }
}
