import React, { Component } from 'react'
import { connect } from 'react-redux'
import PropTypes from 'prop-types'

import axios from 'axios'
import Cookies from 'universal-cookie'

import config from '../config'
import { loginUser } from '../actions/userActions'
import { UserPropTypes } from '../reducers/reducers'

const cookies = new Cookies()

class PriceLogin extends Component {
  constructor(props) {
    super(props)

    this.state = {
      user: '',
      password: '',
      exceptionMessage: '',
      loading: true,
      agreeWithTerms: false
    }

    this.render = this.render.bind(this)
    this.handleClick = this.handleClick.bind(this)
    this.onEnterKeyPressed = this.onEnterKeyPressed.bind(this)
    this.handleAgreeWithTerms = this.handleAgreeWithTerms.bind(this)
  }

  componentWillMount() {
    let tokenUser = cookies.get('tokenUser')
    if (tokenUser === undefined || tokenUser === null || tokenUser === '') {
      this.setState({ loading: false })
      return
    }

    let token = tokenUser.split('|')[0]
    let user = tokenUser.split('|')[1]
    axios.get(config.apiBaseUrl + '/token/', { 'headers': { 'Auth-Token': token } })
      .then(response => {
        if (response.data === 'True') {
          let d = new Date()
          d.setTime(d.getTime() + (
            9 * 60 * 1000))
          cookies.set('tokenUser', tokenUser, { expires: d })
          this.setState({ loading: false })
          this.props.loginUser({ username: user, token: token })
        } else {
          cookies.remove('tokenUser')
          this.setState({ loading: false })
        }
      })
      .catch(() => {
        this.setState({
          loading: false,
          exceptionMessage: 'Erro ao recuperar token'
        })
      })
  }

  handleClick() {
    this.setState({
      exceptionMessage: ''
    })

    if (this.state.user === '') {
      this.setState({
        exceptionMessage: 'Digite seu usuário'
      })
      return
    }

    if (this.state.password === '') {
      this.setState({
        exceptionMessage: 'Digite sua senha'
      })
      return
    }

    axios({
      method: 'post',
      url: config.apiBaseUrl + '/login/?username=' + this.state.user + '&password=' + this.state.password
    })
    .then(response => {
      let d = new Date()
      d.setTime(d.getTime() + (9 * 60 * 1000))
      cookies.set('tokenUser', response.data + '|' + this.state.user, { expires: d })
      this.props.loginUser({ username: this.state.user, token: response.data })

      this.setState({ user: '', password: '' })
    })
    .catch(error => {
      if (error.response !== undefined && error.response.status === 401) {
        this.setState({
          exceptionMessage: 'Usuário ou senha inválido(s)'
        })
      } else if (error.response !== undefined && error.response.status === 403) {
        this.setState({
          exceptionMessage: 'Usuário sem permissão de acesso'
        })
      } else {
        this.setState({
          exceptionMessage: 'Erro ao logar'
        })
      }
    })
  }

  handleAgreeWithTerms() {
    this.setState({
      agreeWithTerms: true
    })
  }

  updateUserValue(evt) {
    this.setState({
      user: evt.target.value,
      exceptionMessage: ''
    })
  }

  updatePasswordValue(evt) {
    this.setState({
      password: evt.target.value,
      exceptionMessage: ''
    })
  }

  renderExceptionMessage() {
    if (this.state.exceptionMessage) {
      return (
        <div className="loginAlert alert alert-danger">
          { this.state.exceptionMessage }
        </div>)
    }
    return ''
  }
  onEnterKeyPressed =(event) =>{
    if (event.key === 'Enter') {
      this.handleClick()
    }
  }
  render() {
    if(!this.state.agreeWithTerms) {
      return (
        <div className="row">
          <div className="loginBox col-lg-8 col-md8 col-xs8">
            <h1>TERMO DE ADESÃO</h1>
            <p>
              A utilização desse serviço de alteração de preços é de total responsabilidade do usuário,
              qualquer alteração realizada deve ser validada e conferida pelo mesmo, sendo este o responsável
              por eventuais perdas de lucros, perda de receita, perda de dados, perdas financeiras ou por
              danos indiretos, especiais, consequenciais, exemplares ou punitivos.
            </p>
            <p>
              O usuário é responsável por manter a senha em sigilo. Qualquer atividade realizada com a utilização
              da mesma ou por algum intermédio é de completa responsabilidade do usuário.
            </p>
            <p>
              Recomendamos que a senha seja alterada constantemente e não seja reutilizada em outros locais.
            </p>
            <button className="btn loginButton" onClick={ this.handleAgreeWithTerms }>Li e Concordo</button>
          </div>
        </div>)
    }

    if (this.state.loading) {
      return (
        <div>Carregando</div>)
    }

    if (this.props.user !== null) {
      return (
        <div className="mainAppItems">{ this.props.children }</div>)
    }

    return (
      <div className="row">
        <div className="col-lg-4 col-md-4 col-xs-4" />
        <div className="loginBox col-lg-4 col-md-4 col-xs-4">
          <h1>LOGIN</h1>

          <div className="form-group">
            <label htmlFor="username">Usuário</label>
            <input type={'text'} id={'username'} autoFocus={true} className="form-control" onKeyPress={this.onEnterKeyPressed} onChange={evt => this.updateUserValue(evt)} placeholder="Digite seu usuário" />
          </div>

          <div className="form-group">
            <label htmlFor="pass">Senha:</label>
            <input type={'password'} id={'pass'} className="form-control" onKeyPress={this.onEnterKeyPressed} onChange={evt => this.updatePasswordValue(evt)} placeholder="Digite sua senha" />
          </div>

          <button className="btn loginButton" onClick={ this.handleClick }>Login</button>

          { this.renderExceptionMessage() }
        </div>
        <div className="col-4" />
      </div>)
  }
}

PriceLogin.propTypes = {
  user: UserPropTypes,
  loginUser: PropTypes.func,
  children: PropTypes.oneOfType([PropTypes.node, PropTypes.node])
}

const mapStateToProps = state => (
  {
    user: state.user
  })

const mapDispatchToProps = dispatch => (
  {
    loginUser: user => dispatch(loginUser(user))
  })

export default connect(mapStateToProps, mapDispatchToProps)(PriceLogin)
