import { GET_PRODUCT_CATEGORIES } from '../actions/productCategoriesActions'

export default function productCategoriesReducer(state = null, action) {
  switch (action.type) {
  case GET_PRODUCT_CATEGORIES:
    return action.categoriesList
  default:
    return state
  }
}
