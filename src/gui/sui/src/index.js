import React from 'react'
import { render } from 'react-dom'
import { Provider } from 'react-redux'

import { IntlProviderContainer } from '3s-posui/core'
import '@fortawesome/fontawesome-free/css/all.css'
import '../style/style.css'

import App from './app'
import { configureStore } from './store'


const store = configureStore({})

render(
  <Provider store={store}>
    <IntlProviderContainer>
      <App/>
    </IntlProviderContainer>
  </Provider>
  , document.querySelector('.container')
)
