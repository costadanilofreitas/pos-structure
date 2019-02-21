import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { FormattedNumber } from 'react-intl'
import CurrencyInput from 'react-currency-input'
import { OverlayTrigger, Tooltip } from 'react-bootstrap'

import { DataPropTypes } from '../reducers/productListReducer'
import { UserPropTypes } from '../reducers/reducers'
import {
  COMBOS,
  RESET_EDITING_PRODUCT,
  SAVE_MODIFIER_REQUEST,
  SAVE_PRODUCT_REQUEST
} from '../common/constants'


class GenericProduct extends Component {
  constructor(props) {
    super(props)
    this.handlePriceOnChange = this.handlePriceOnChange.bind(this)
    this.handleCancelOnClick = this.handleCancelOnClick.bind(this)
    this.handleEditOnClick = this.handleEditOnClick.bind(this)
  }

  state = {
    errorInputValue: false,
    newPrice: this.props.product.price,
    editing: false
  }

  handlePriceOnChange(event) {
    this.setState({ newPrice: event })
  }

  handlePriceSave = () => {
    this.setState({ editing: true })
    let priceValue = this.state.newPrice.replace(',', '.')
    let moneyRegex = '\\d+.\\d{2}$'

    if (this.state.newPrice.match(moneyRegex) === null ||
        Number(priceValue) < 0.0 || Number(priceValue) > 999.99) {
      this.setState({ errorInputValue: true })
      return
    }
    if (this.props.classCode !== undefined) {
      this.props.savingModifier(
        this.props.product,
        Number(priceValue),
        this.props.user.token,
        this.props.classCode)
      return
    }

    this.props.savingProduct(
      this.props.dataRequest,
      this.props.product,
      Number(priceValue),
      this.props.user.token)
  }

  handleCancelOnClick() {
    this.setState({
      editing: false,
      newPrice: Number(this.props.product.price),
      errorInputValue: false
    })
  }

  handleEditOnClick() {
    this.setState({
      editing: true,
      newPrice: this.props.product.price.toFixed(2).toString().replace('.', ','),
      errorInputValue: false
    })
  }

  componentWillMount() {
    this.setState({ newPrice: this.props.product.price })
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.product.saveError !== undefined && nextProps.product.saveError !== false) {
      this.setState({ editing: true })
      return
    }
    if (nextProps.product.saved && this.state.editing) {
      this.setState({ editing: false })
    }
  }

  render() {
    let productPartCodeHtml = this.props.product.partCode
    let productNameHtml = this.props.product.productName

    return (
      <tr>
        { this.props.dataRequest === COMBOS &&
          <td className="bodyTable bodyTableCombo"> { this.props.product.comboPartCode } </td>
        }
        <td className="bodyTable" dangerouslySetInnerHTML={{ __html: (productPartCodeHtml) }} />

        <td className="bodyTable" dangerouslySetInnerHTML={{ __html: (productNameHtml) }} />

        { this.props.dataRequest === COMBOS &&
          <td className="bodyTable">
            <FormattedNumber value={ this.props.product.product_price } style="currency" currency="BRL"/>
          </td>
        }
        <td className="bodyTable" >
          <FormattedNumber value={ this.props.product.price } style="currency" currency="BRL"/>
        </td>
      </tr>
    )
  }
}

GenericProduct.propTypes = {
  product: DataPropTypes,
  user: UserPropTypes,
  savingProduct: PropTypes.func,
  dataRequest: PropTypes.string,
  savingModifier: PropTypes.func,
  classCode: PropTypes.number,
  hideEdit: PropTypes.bool
}

GenericProduct.defaultProps = {
  product: null

}

const mapStateToProps = (state) => {
  return {
    user: state.user
  }
}

const mapDispatchToProps = dispatch => {
  return {
    savingProduct: (dataRequest, product, newPrice, token) => dispatch({
      type: SAVE_PRODUCT_REQUEST,
      product: product,
      dataRequest: dataRequest,
      newPrice: newPrice,
      token: token
    }),
    savingModifier: (product, newPrice, token, classCode) => dispatch({
      type: SAVE_MODIFIER_REQUEST,
      product: product,
      newPrice: newPrice,
      token: token,
      classCode: classCode
    }),
    cancellingProduct: (product) => dispatch({ type: RESET_EDITING_PRODUCT, product: product })
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(GenericProduct)

