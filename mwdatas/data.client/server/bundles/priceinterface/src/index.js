import React from 'react'
import { render } from 'react-dom'
import { Provider } from 'react-redux'
import { HashRouter } from 'react-router-dom'
import { addLocaleData, IntlProvider } from 'react-intl'
import en from 'react-intl/locale-data/en'
import pt from 'react-intl/locale-data/pt'

import 'font-awesome/css/font-awesome.css'
import '../style/components/priceLogin.css'
import '../style/components/pricePublish.css'
import '../style/components/genericList.css'
import '../style/components/modifier.css'
import '../style/styles.css'
import '../node_modules/bootstrap/dist/css/bootstrap.min.css'
import '../node_modules/react-table/react-table.css'

import configureStore from './store'

import App from './app/App'

addLocaleData([...en, ...pt])
const store = configureStore({})

render(
  <Provider store={ store }>
    <IntlProvider locale="pt-BR">
      <HashRouter>
        <App/>
      </HashRouter>
    </IntlProvider>
  </Provider>

  , document.getElementById('root')
)
