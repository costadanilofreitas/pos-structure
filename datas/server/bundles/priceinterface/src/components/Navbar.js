import React, { Component } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios/index'
import { connect } from 'react-redux'
import PropTypes from 'prop-types'
import withRouter from 'react-router-dom/es/withRouter'

import {
  COMBOS_LINK,
  MODIFIERS_LINK,
  PUBLISH_LINK,
  EXPORT_LINK
} from '../common/constants'
import config from '../config'
import { UserPropTypes } from '../reducers/reducers'
import { setProductCategories } from '../actions/productCategoriesActions'


class Navbar extends Component {
  componentWillMount() {
    if (this.props.categoriesList == null) {
      let token = this.props.user.token

      axios.get(config.apiBaseUrl + '/priceList/productCategories/', { 'headers': { 'Auth-Token': token } })
        .then(response => {
          this.props.setProductCategories(response.data)
        })
    }
  }

  componentWillUnmount() {
    this.props.setProductCategories(null)
  }

  importAll(r) {
    let images = {}
    r.keys().map((item) => {
      images[item.replace('./', '')] = r(item)
      return null
    })
    return images
  }

  render() {
    const images = this.importAll(require.context('../../images', false, /\.(png|jpe?g|svg)$/))

    return (
      <ul>
        {
          this.props.categoriesList !== null &&
          this.props.categoriesList.map(function (obj, pos) {
            let backgroundImageActive = (window.location.href.endsWith('/' + obj.name) || (window.location.href.endsWith('/') && pos === 0)) ? '_active.png' : '.png'

            return (
              <li key={obj.name} className={ (window.location.href.endsWith('/' + obj.name) || (window.location.href.endsWith('/') && pos === 0)) && ('active') }>
                <Link to={ '/priceList/' + obj.name }>
                  <span className="optionsMenuItem" style ={ { background: 'url(' + images[obj.name + backgroundImageActive] + ') no-repeat' } }/>
                  <span className="hidden-xs">{ obj.title }</span></Link>
              </li>
            )
          })
        }
        <li className={ (window.location.href.endsWith('/combos') || (window.location.href.endsWith('/') && (this.props.categoriesList === null || this.props.categoriesList.length === 0))) && 'active' }>
          <Link to={ COMBOS_LINK }><span className="optionsMenuItem combosImage"/>
            <span className="hidden-xs">Combos</span></Link>
        </li>
        <li className={ window.location.href.endsWith('/modifiers') && 'active' }>
          <Link to={ MODIFIERS_LINK }><span className="optionsMenuItem modificadoresImage"/>
            <span className="hidden-xs">Adicionais</span></Link>
        </li>
        <li className={ window.location.href.endsWith('/publish') && 'active' }>
          <Link to={ PUBLISH_LINK }><span className="optionsMenuItem publicarImage"/>
            <span className="hidden-xs">Publicar</span></Link>
        </li>
        <li className={ window.location.href.endsWith('/export') && 'active' }>
          <Link to={ EXPORT_LINK }><span className="optionsMenuItem exportImage"/>
            <span className="hidden-xs">Exportar Preços</span></Link>
        </li>
      </ul>
    )
  }
}

Navbar.propTypes = {
  user: UserPropTypes,
  setProductCategories: PropTypes.func,
  categoriesList: PropTypes.array
}

const mapStateToProps = state => ({
  user: state.user,
  categoriesList: state.productCategories
})

const mapDispatchToProps = dispatch => ({
  setProductCategories: categoriesList => dispatch(setProductCategories(categoriesList))
})

export default withRouter(connect(mapStateToProps, mapDispatchToProps)(Navbar))
