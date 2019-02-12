import React from 'react'
import { render } from 'react-dom'
import { Provider } from 'react-redux'
import { addLocaleData } from 'react-intl'
import en from 'react-intl/locale-data/en'
import pt from 'react-intl/locale-data/pt'
import { IntlProviderContainer } from 'posui/core'
import 'font-awesome/css/font-awesome.css'
import '../style/style.css'
import { App } from './app'
import { configureStore } from './store'

addLocaleData([...en, ...pt])

const store = configureStore({})

render(
  <Provider store={store}>
    <IntlProviderContainer>
      <App />
    </IntlProviderContainer>
  </Provider>
  , document.querySelector('.container'))
