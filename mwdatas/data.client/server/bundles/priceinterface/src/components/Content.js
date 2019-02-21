import React, { Component } from 'react'
import { Route, Switch } from 'react-router-dom'
import { connect } from 'react-redux'
import withRouter from 'react-router-dom/es/withRouter'
import PropTypes from 'prop-types'

import PricePublish from './PricePublish'
import GenericList from './GenericList'
import Modifiers from './Modifiers'
import NotFound from './NotFound'
import PriceExport from './PriceExport'

import {
  COMBOS,
  COMBOS_LINK,
  MODIFIERS_LINK,
  PRODUCTS,
  PUBLISH_LINK,
  EXPORT_LINK
} from '../common/constants'


class Content extends Component {
  render() {
    let pageTitle = ''

    if (this.props.categoriesList !== null) {
      this.props.categoriesList.map(function (obj) {
        if (window.location.href.endsWith('/' + obj.name)) {
          pageTitle = obj.title
        }

        return null
      })
    }

    if (pageTitle === '') {
      if (window.location.href.endsWith('/')) {
        pageTitle = 'Combos'
        if (this.props.categoriesList !== null && this.props.categoriesList.length > 0) {
          pageTitle = this.props.categoriesList[0].title
        }
      } else if (window.location.href.endsWith('/combos')) {
        pageTitle = 'Combos'
      } else if (window.location.href.endsWith('/modifiers')) {
        pageTitle = 'Adicionais'
      } else if (window.location.href.endsWith('/publish')) {
        pageTitle = 'Publicar'
      } else if (window.location.href.endsWith('/export')) {
        pageTitle = 'Exportar Preços'
      }
    }

    let defaultRoute = <Route exact path="/"
                               render ={ () => <GenericList dataRequest={COMBOS}/>}/>

    if (this.props.categoriesList !== null && this.props.categoriesList.length > 0) {
      defaultRoute = <Route exact path="/"
                       render ={ () =>
                         <GenericList
                           dataRequest={PRODUCTS}
                           productCategory={this.props.categoriesList[0].name}/>}
                      />
    }

    return (
      <div className="content">
        <h1 className="pageTitle">
          {pageTitle.toUpperCase()}
        </h1>
        <Switch>
          {defaultRoute}
          {
            this.props.categoriesList !== null &&
            this.props.categoriesList.map(function (obj) {
              return (
                <Route key={obj.name} path={'/priceList/' + obj.name} render ={ () => <GenericList dataRequest={PRODUCTS} productCategory={obj.name}/>}/>
              )
            })
          }
          <Route path={COMBOS_LINK} render ={ () => <GenericList dataRequest={COMBOS}/>}/>
          <Route path={MODIFIERS_LINK} component={ Modifiers } />
          <Route path={PUBLISH_LINK} component={ PricePublish }/>
          <Route path={EXPORT_LINK} component={ PriceExport }/>
          <Route component={NotFound}/>
        </Switch>
      </div>
    )
  }
}

Content.propTypes = {
  categoriesList: PropTypes.array
}

const mapStateToProps = state => ({
  categoriesList: state.productCategories
})

export default withRouter(connect(mapStateToProps)(Content))
