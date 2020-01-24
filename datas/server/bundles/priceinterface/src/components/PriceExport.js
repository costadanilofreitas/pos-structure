import React, { Component } from 'react'
import { CSVLink } from 'react-csv'
import axios from 'axios/index'
import config from '../config'
import PropTypes from 'prop-types'
import { UserPropTypes } from '../reducers/reducers'
import { logoutUser } from '../actions/userActions'
import { connect } from 'react-redux'

class PriceExport extends Component {

  constructor(props) {
    super(props)

    this.state = {
      exportItems: '',
      exportError: false
    }
  }

  componentWillMount() {
    let token = this.props.user.token

    axios.get(config.apiBaseUrl + '/price/exportPrices/', { 'headers': { 'Auth-Token': token } })
      .then(response => {
        this.setState({
          exportItems: response.data,
          exportError: false
        })
      }, error => {
        if (error.response !== undefined && error.response.status === 401) {
          this.props.logoutUser(this.props.user.token)
        } else if (error.response !== undefined && error.response.status === 403) {
          this.props.logoutUser(this.props.user.token)
        } else {
          this.setState({
            exportError: true
          })
        }
      })
  }

  yyyymmddDateTimeNow() {
    let dateNow = new Date()

    let mm = dateNow.getMonth() + 1
    let dd = dateNow.getDate()

    return [dateNow.getFullYear(),
      '_',
      (mm > 9 ? '' : '0') + mm,
      '_',
      (dd > 9 ? '' : '0') + dd,
      '_',
      dateNow.getHours(),
      '_',
      dateNow.getMinutes(),
      '_',
      dateNow.getSeconds()
    ].join('')
  }

  render() {
    let headers = [
      { label: 'Código do Produto', key: 'part_code' },
      { label: 'Código do Combo', key: 'combo_part_code' },
      { label: 'Preço', key: 'price' },
      { label: 'Nome', key: 'product_name' }
    ]

    return (
      <div className="pricePublishContent">
        <p>
          Deseja exportar os preços em um arquivo CSV?
        </p>
        <p className="publishOptions">
          <CSVLink
            data={ this.state.exportItems }
            headers={ headers }
            filename={ 'Precos_' + this.yyyymmddDateTimeNow() + '.csv' } >
              EXPORTAR
          </CSVLink>
        </p>
      </div>
    )
  }
}

PriceExport.propTypes = {
  user: UserPropTypes,
  logoutUser: PropTypes.func
}

const mapStateToProps = state => ({
  user: state.user
})

const mapDispatchToProps = dispatch => ({
  logoutUser: token => dispatch(logoutUser(token))
})

export default connect(mapStateToProps, mapDispatchToProps)(PriceExport)
