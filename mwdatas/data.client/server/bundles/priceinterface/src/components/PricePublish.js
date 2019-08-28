import React, { Component } from 'react'
import { connect } from 'react-redux'
import PropTypes from 'prop-types'
import axios from 'axios'
import config from '../config'
import { logoutUser } from '../actions/userActions'
import { UserPropTypes } from '../reducers/reducers'
import PricePublishModal from './PricePublishModal'


class PricePublish extends Component {

  constructor(props) {
    super(props)

    this.state = {
      sourceDatabaseHasChanges: false,
      targetDatabaseHasChanges: false,
      responseMessage: '',
      publishing: false,
      publishEnded: false,
      errorMessage: '',
      revertingChanges: false,
      changesReverted: false,
      loading: true,
      changedItems: '',
      showModal: false
    }
    this.handleClickApply = this.handleClickApply.bind(this)
    this.handleClickRevert = this.handleClickRevert.bind(this)
    this.handleClickShowModal = this.handleClickShowModal.bind(this)
  }

  componentWillMount() {
    let token = this.props.user.token
    this.setState({
      sourceDatabaseHasChanges: false,
      targetDatabaseHasChanges: false,
      errorMessage: '',
      loading: true
    })

    axios.get(config.apiBaseUrl + '/price/databaseHasChanges/', { 'headers': { 'Auth-Token': token } })
      .then(response => {
        this.setState({
          targetDatabaseHasChanges: true,
          loading: false,
          changedItems: response.data })

        if (response.data &&
          this.state.changedItems.products &&
          this.state.changedItems.products.length > 0) {
          this.setState({ showProducts: true })
        } else if (this.state.changedItems &&
          this.state.changedItems.combos &&
          this.state.changedItems.combos.length > 0) {
          this.setState({ showCombos: true })
        } else if (this.state.changedItems &&
          this.state.changedItems.modifiers &&
          this.state.changedItems.modifiers.length > 0) {
          this.setState({ showModifiers: true })
        }

        if (this.state.productCategory === '' || this.state.productCategory === undefined) {
          if (this.state.changedItems.products.filter(prod => prod.category === 'sandwich').length > 0) {
            this.setState({ productCategory: 'sandwich' })
          } else if (this.state.changedItems.products.filter(prod => prod.category === 'accompaniment').length > 0) {
            this.setState({ productCategory: 'accompaniment' })
          } else if (this.state.changedItems.products.filter(prod => prod.category === 'beverage').length > 0) {
            this.setState({ productCategory: 'beverage' })
          } else if (this.state.changedItems.products.filter(prod => prod.category === 'desert').length > 0) {
            this.setState({ productCategory: 'desert' })
          }
        }
      }, error => {
        if (error.response !== undefined && error.response.status === 401) {
          this.props.logoutUser(this.props.user.token)
        } else if (error.response !== undefined && error.response.status === 403) {
          this.props.logoutUser(this.props.user.token)
        } else if (error.response !== undefined && error.response.status === 406) {
          this.setState({ sourceDatabaseHasChanges: true })
        } else if (error.response !== undefined && error.response.status !== 304) {
          this.setState({ errorMessage: 'Erro ao verificar banco: ' })
        }
        this.setState({ loading: false })
      })
  }

  render() {
    if (this.state.loading) {
      return (
        <div className="pricePublishContent">
          <p>Analisando se houve alguma alteração</p>
        </div>
      )
    }
    if (this.state.errorMessage !== '') {
      return (
        <div className="pricePublishContent">
          <p>{this.state.errorMessage}</p>
        </div>
      )
    }

    if (this.state.publishing) {
      return (
        <div className="pricePublishContent">
          <p>Aplicando alterações</p>
        </div>
      )
    }

    if (this.state.publishEnded) {
      if (this.state.errorMessage !== '') {
        return (
          <div className="pricePublishContent">
            <p>{this.state.errorMessage}</p>
          </div>
        )
      }

      return (
        <div className="pricePublishContent">
          <p>Alteração de preço aplicada</p>
        </div>
      )
    }

    if (this.state.revertingChanges) {
      return (
        <div className="pricePublishContent">
          <p>Desfazendo as alterações</p>
        </div>
      )
    }

    if (this.state.changesReverted) {
      if (this.state.errorMessage !== '') {
        return (
          <div className="pricePublishContent">
            <p>{this.state.errorMessage}</p>
          </div>
        )
      }

      return (
        <div className="pricePublishContent">
          <p>Alteração desfeita</p>
        </div>
      )
    }

    if (this.state.sourceDatabaseHasChanges) {
      return (
        <div className="pricePublishContent">
          <p>
            Houve alterações no banco original. Deseja atualizar o banco da aplicação?
            (Todas as alterações serão perdidas e você será deslogado)
          </p>
          <p className="publishOptions">
            <button onClick={ this.handleClickRevert.bind(this, true) }>ATUALIZAR</button>
          </p>
        </div>
      )
    }

    if (!this.state.targetDatabaseHasChanges) {
      return (
        <div className="pricePublishContent">
          <p>Nenhuma alteração a ser publicada</p>
        </div>
      )
    }

    return (
      <div className="pricePublishContent">
        <p>Aplicar as alterações? (Requer uma reinicialização do sistema)</p>
        <p className="publishChangesModal" onClick={ this.handleClickShowModal }>Verificar as alterações</p>
        <p className="publishOptions">
          <button onClick={ this.handleClickRevert.bind(this, false) }>DESFAZER</button>
          <button onClick={ this.handleClickApply.bind(this) }>APLICAR</button>
        </p>
        <p>{ this.state.responseMessage }</p>

        <PricePublishModal
          changedItems = {this.state.changedItems}
          showModal = {this.state.showModal}
          showProducts = {this.state.showProducts}
          showModifiers = {this.state.showModifiers}
          showCombos = {this.state.showCombos}
          productCategory = {this.state.productCategory} />
      </div>
    )
  }

  handleClickApply() {
    let token = this.props.user.token

    this.setState({
      publishing: true,
      errorMessage: ''
    })

    axios({
      method: 'post',
      url: config.apiBaseUrl + '/price/publish/',
      headers: { 'Auth-Token': token }
    })
      .then(() => {
        this.setState({
          publishing: false,
          publishEnded: true
        })
      })
      .catch(error => {
        if (error.response.status === 401) {
          this.props.logoutUser(this.props.user.token)
        } else if (error.response.status === 403) {
          this.props.logoutUser(this.props.user.token)
        } else {
          this.setState({ errorMessage: 'Erro ao aplicar atualizações' })
        }
      })
  }

  handleClickRevert(logout) {
    let token = this.props.user.token

    this.setState({ revertingChanges: true, errorMessage: '' })

    axios({ method: 'post',
      url: config.apiBaseUrl + '/price/publishRevert/',
      headers: { 'Auth-Token': token }
    })
      .then(() => {
        this.setState({ revertingChanges: false, changesReverted: true })

        if (logout) {
          this.props.logoutUser(token)
        }
      })
      .catch(error => {
        if (error.response.status === 401) {
          this.props.logoutUser(this.props.user.token)
        } else if (error.response.status === 403) {
          this.props.logoutUser(this.props.user.token)
        } else {
          this.setState({ errorMessage: 'Erro ao desfazer as atualizações' + error })
        }
      })
  }

  handleClickShowModal() {
    this.setState({
      showModal: true
    })
  }
}

PricePublish.propTypes = {
  user: UserPropTypes,
  logoutUser: PropTypes.func
}

const mapStateToProps = state => ({
  user: state.user
})

const mapDispatchToProps = dispatch => ({
  logoutUser: token => dispatch(logoutUser(token))
})

export default connect(mapStateToProps, mapDispatchToProps)(PricePublish)
