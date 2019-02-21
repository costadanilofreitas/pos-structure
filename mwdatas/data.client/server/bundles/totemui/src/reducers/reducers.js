import { combineReducers } from 'redux';
import selectedScreenReducer from './selectScreenReducer'
import orderReducer from './orderReducer'
import paymentReducer from './paymentReducer'
import titleReducer from './titleReducer'
import selectedSideMenuReducer from './selectedSideMenuReducer'
import modalReducer from './modalReducer'
import selectedSubScreenReducer from './selectedSubScreenReducer'
import stringsReducer from './stringsReducer'
import acumulateValueReducer from './acumulateValueReducer'
import categoryReducer from './categoryReducer'
import productReducer from './productReducer'
import headerReducer from './headerReducer'
import errorReducer from './errorReducer'
import configReducer from './configReducer'
import categoryScrollReducer from './categoryScrollReducer'
import couponDataReducer from './couponDataReducer'



const rootReducer = combineReducers({
    selectedScreen: selectedScreenReducer,
    selectedSubScreen: selectedSubScreenReducer,
    order: orderReducer,
    payment: paymentReducer,
    title: titleReducer,
    selectedSideMenu: selectedSideMenuReducer,
    modalState: modalReducer,
    strings: stringsReducer,
    acumulateValue: acumulateValueReducer,
    category: categoryReducer,
    product: productReducer,
    header: headerReducer,
    error: errorReducer,
    config: configReducer,
    categoryScroll: categoryScrollReducer,
    couponData: couponDataReducer
});

export default rootReducer