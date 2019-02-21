import React, { Component } from 'react'
import { connect } from 'react-redux'
import ReactTable from 'react-table'
import CurrencyInput from 'react-currency-input'
import PropTypes from 'prop-types'
import { OverlayTrigger, Tooltip, Modal } from 'react-bootstrap'
import { FormattedNumber } from 'react-intl'

import { cancelEditingItem, changePriceItem, editingItem } from '../actions/genericListActions'

import {
  COMBOS,
  GET_ALL_DATA_REQUEST,
  SAVE_MODIFIER_REQUEST,
  SAVE_PRODUCT_REQUEST
} from '../common/constants'
import { logoutUser } from '../actions/userActions'
import { UserPropTypes } from '../reducers/reducers'
import { GenericDataPropTypes } from '../reducers/productListReducer'


class GenericList extends Component {
  constructor(props) {
    super(props)
    this.handlePriceOnChange = this.handlePriceOnChange.bind(this)
    this.handleCancelOnClick = this.handleCancelOnClick.bind(this)
    this.handleEditOnClick = this.handleEditOnClick.bind(this)
    this.handleChangeItemsModalClose = this.handleChangeItemsModalClose.bind(this)
  }


  state = {
    originalPrice: 0,
    newPrice: 0,
    errorInputValue: false,
    productSaveError: 0,
    comboSaveError: 0,
    previousPartCode: 0,
    previousComboPartCode: 0,
    priceComboHigherProduct: false,
    priceComboHigherProductObjectToSave: null,
    priceComboHigherProductPriceToSave: 0,
    editingPartCode: 0,
    editingComboPartCode: 0
  }

  handleEditOnClick(e, partCode, comboPartCode) {
    this.setState({
      editingPartCode: partCode,
      editingComboPartCode: comboPartCode
    })

    this.props.editingItem(partCode, comboPartCode)

    let originalPrice = 0
    for (let i = 0; i < this.props.genericData.data.length; i++) {
      if (partCode !== undefined && this.props.genericData.data[i].partCode === partCode) {
        originalPrice = this.props.genericData.data[i].price
      } else if (comboPartCode !== undefined &&
        this.props.genericData.data[i].comboPartCode === comboPartCode) {
        originalPrice = this.props.genericData.data[i].price
      }
    }

    this.setState({
      comboSaveError: 0,
      productSaveError: 0,
      errorInputValue: false,
      originalPrice: originalPrice,
      previousPartCode: partCode,
      previousComboPartCode: comboPartCode
    })
  }

  handleCancelOnClick(e, partCode, comboPartCode) {
    this.props.cancelEditingItem(partCode, comboPartCode)

    this.setState({
      comboSaveError: 0,
      productSaveError: 0
    })
  }

  handlePriceOnChange(e) {
    this.setState({ newPrice: Number(e.target.value.replace('.', '').replace(',', '.')) })
  }

  handlePriceSave = (e, partCode, comboPartCode) => {
    let objectToSave = ''
    let priceValue = this.state.newPrice
    let moneyRegex = '\\d+.\\d{2}$'

    this.setState({ errorInputValue: false })

    if (priceValue === this.state.originalPrice) {
      this.props.cancelEditingItem(partCode, comboPartCode)
      return
    }

    if (String(this.state.newPrice.toFixed(2)).match(moneyRegex) === null ||
      Number(priceValue) < 0.0 || Number(priceValue) > 999.99) {
      this.setState({ errorInputValue: true })

      this.props.changePriceItem(
        partCode,
        comboPartCode,
        this.state.originalPrice
      )

      return
    }

    for (let i = 0; i < this.props.genericData.data.length; i++) {
      if ((partCode !== undefined &&
          this.props.genericData.data[i].partCode === partCode) ||
        (comboPartCode !== undefined &&
          this.props.genericData.data[i].comboPartCode === comboPartCode)) {
        objectToSave = this.props.genericData.data[i]
        objectToSave.editing = false
      }
    }

    if (this.props.dataRequest === 'COMBOS' && this.state.newPrice > objectToSave.product_price) {
      this.setState({
        priceComboHigherProduct: true,
        priceComboHigherProductObjectToSave: objectToSave,
        priceComboHigherProductPriceToSave: this.state.newPrice
      })
    } else if (this.props.dataRequest === 'PRODUCTS' || this.props.dataRequest === 'COMBOS') {
      this.props.savingProduct(
        this.props.dataRequest,
        objectToSave,
        Number(priceValue),
        this.props.user.token)
    } else if (this.props.dataRequest.toString().indexOf('/modifier/') > 0) {
      this.props.savingModifier(
        objectToSave,
        Number(priceValue),
        this.props.user.token,
        this.props.classCode)
    }

    this.props.cancelEditingItem(partCode, comboPartCode)
  }

  handlePriceSaveModalConfirm() {
    this.props.savingProduct(
      this.props.dataRequest,
      this.state.priceComboHigherProductObjectToSave,
      this.state.priceComboHigherProductPriceToSave,
      this.props.user.token)

    this.handleChangeItemsModalClose()
  }

  componentWillMount() {
    this.props.onRequestData(
      this.props.dataRequest,
      this.props.user.token,
      this.props.productCategory
    )
  }

  componentDidUpdate() {
    if (this.props.genericData
      && this.props.genericData.loadingData !== undefined
      && this.props.genericData.loadingData === false
      && this.props.genericData.data
      && this.props.genericData.data.response
      && this.props.genericData.data.response.status === 401) {
      this.props.logoutUser(this.props.user.token)
    }
  }

  componentWillReceiveProps(nextProps) {
    if (this.props.dataRequest !== nextProps.dataRequest ||
      this.props.productCategory !== nextProps.productCategory) {
      this.props.onRequestData(
        nextProps.dataRequest,
        this.props.user.token,
        nextProps.productCategory
      )
    } else if (this.props.genericData.data !== nextProps.genericData.data &&
      nextProps.genericData.newPrice !== undefined &&
      nextProps.genericData.originalPrice !== undefined) {
      this.setState({ newPrice: nextProps.genericData.newPrice })

      if (this.state.originalPrice === 0) {
        this.setState({ originalPrice: nextProps.genericData.originalPrice })
      }
    }

    if (nextProps.genericData.priceChanged != null &&
      nextProps.genericData.priceChanged.line != null &&
      nextProps.genericData.priceChanged.line.saveError !== false) {
      if (nextProps.genericData.priceChanged.line.comboPartCode !== undefined) {
        this.props.editingItem(undefined, nextProps.genericData.priceChanged.line.comboPartCode)
        this.setState({ comboSaveError: nextProps.genericData.priceChanged.line.comboPartCode })
      } else {
        this.props.editingItem(nextProps.genericData.priceChanged.line.partCode, undefined)
        this.setState({ productSaveError: nextProps.genericData.priceChanged.line.partCode })
      }
    }
  }

  onEnterKeyPressed = (e) => {
    if (e.target.className === 'editingInput') {
      if (e.key === 'Enter') {
        this.setState({ newPrice: Number(e.target.value.replace('.', '').replace(',', '.')) },
          function () {
            this.handlePriceSave(e, this.state.editingPartCode, this.state.editingComboPartCode)
          }
        )
      } else if (e.key === 'Escape') {
        this.props.cancelEditingItem(this.state.editingPartCode, this.state.editingComboPartCode)
      }
    }
  }

  handleChangeItemsModalClose() {
    this.setState({ priceComboHigherProduct: false })
  }

  componentDidMount() {
    window.addEventListener('keydown', this.onEnterKeyPressed)
  }

  componentWillUnmount() {
    window.removeEventListener('keydown', this.onEnterKeyPressed)
  }

  render() {
    let data = this.props.genericData.data
    let columns = []
    let rowsToShow = 5

    if (data !== undefined) {
      rowsToShow = data.length < 10 ? 5 : 10
    }

    const tooltip = (
      <Tooltip id="tooltip">
        O preço do item foi alterado
      </Tooltip>
    )

    if (data !== undefined && data.length > 0) {
      for (let i = 0; i < data.length; i++) {
        if (this.state.productSaveError !== 0 &&
            data[i].partCode === this.state.productSaveError) {
          data[i].errorToSave = 'error'
        } else {
          data[i].errorToSave = ''
        }

        if (this.props.dataRequest === 'COMBOS') {
          if (this.state.comboSaveError !== 0 &&
              data[i].comboPartCode === this.state.comboSaveError) {
            data[i].errorToSave = 'error'
          } else {
            data[i].errorToSave = ''
          }

          data[i].concatPartCode = data[i].partCode
          data[i].concatProductName = data[i].productName
          data[i].concatPrice = data[i].price.toFixed(2)

          let totalComboPrice = data[i].price
          if (data[i].combo_products !== undefined) {
            for (let j = 0; j < data[i].combo_products.length; j++) {
              data[i].concatPartCode += '|' + data[i].combo_products[j].partCode
              data[i].concatProductName += '|' + data[i].combo_products[j].productName
              data[i].concatPrice += '|' + data[i].combo_products[j].price.toFixed(2)
              totalComboPrice += data[i].combo_products[j].price
            }
          }

          data[i].totalComboPrice = totalComboPrice
        }
      }
    }

    if (this.props.dataRequest === COMBOS) {
      columns.push(
        {
          Header: 'Código Combo',
          accessor: 'comboPartCode',
          headerClassName: 'comboPartCodeColumn',
          className: 'comboPartCodeColumn',
          Cell: row => (
            <div>
              {row.value}
            </div>
          )
        },
        {
          Header: 'Código Produto',
          accessor: 'concatPartCode',
          headerClassName: 'comboProductCodeColumn',
          className: 'comboProductCodeColumn',
          Cell: row => (
            <div>
              {(typeof row.value) === 'string' && row.value.split('|').map((obj) =>
                <p key={obj}>{obj}</p>
              )}
            </div>
          )
        },
        {
          Header: 'Nome',
          accessor: 'concatProductName',
          headerClassName: 'comboProductsNameColumn',
          className: 'comboProductsNameColumn',
          Cell: row => (
            <div>
              {(typeof row.value) === 'string' && row.value.split('|').map((obj) =>
                <p key={obj}>{obj}</p>
              )}
            </div>
          )
        },
        {
          Header: 'Preço Individual',
          accessor: 'product_price',
          headerClassName: 'comboProductPriceColumn',
          className: 'comboProductPriceColumn',
          Cell: cellInfo => (
                <div>
                  { cellInfo.row.product_price !== undefined &&
                    <FormattedNumber value={ cellInfo.row.product_price } style="currency" currency="BRL"/>
                  }
                </div>
          )
        },
        {
          Header: 'Preço no Combo',
          accessor: 'concatPrice',
          headerClassName: 'comboProductsPriceColumn',
          className: 'comboProductsPriceColumn',
          Cell: cellInfo => (
            <div className={cellInfo.row.editing && 'editingPrice'}>
              {
                !cellInfo.row.editing ?
                  cellInfo.row.concatPrice.split('|').map((obj, pos) =>
                    <p key={cellInfo.row.concatPartCode.toString().indexOf('|') > 0 ? cellInfo.row.comboPartCode + cellInfo.row.concatPartCode.split('|')[pos] + obj : pos}><FormattedNumber value={ obj } style="currency" currency="BRL"/></p>
                  ) :
                <CurrencyInput value={ this.state.newPrice }
                  className="editingInput"
                  onKeyPress={(e) => this.onEnterKeyPressed(e)}
                  onBlur={ (e) => this.handlePriceOnChange(
                    e, cellInfo.row.partCode, cellInfo.row.comboPartCode
                  )}
                  decimalSeparator=","
                  thousandSeparator="."
                  autoFocus={true}
                />
              }
              {
                cellInfo.row.editing &&
                cellInfo.row.concatPrice.split('|').map((obj, pos) =>
                  pos !== 0 && <p key={cellInfo.row.concatPartCode.toString().indexOf('|') > 0 ? cellInfo.row.comboPartCode + cellInfo.row.concatPartCode.split('|')[pos] + obj : pos}><FormattedNumber value={ obj } style="currency" currency="BRL"/></p>
                )
              }
            </div>
          )
        },
        {
          Header: 'Total Combo',
          accessor: 'totalComboPrice',
          headerClassName: 'comboTotalPriceColumn',
          className: 'comboTotalPriceColumn',
          Cell: row => (
            <div>
              <FormattedNumber value={ row.value.toFixed(2) } style="currency" currency="BRL"/>
            </div>
          )
        }
        )
    } else {
      columns.push(
        {
          Header: 'Código',
          accessor: 'partCode',
          headerClassName: 'partCodeColumn',
          className: 'partCodeColumn'
        },
        {
          Header: 'Nome',
          accessor: 'productName',
          headerClassName: 'productsNameColumn',
          className: 'productsNameColumn'
        },
        {
          Header: 'Preço',
          accessor: 'price',
          headerClassName: 'productsPriceColumn',
          className: 'productsPriceColumn',
          Cell: cellInfo => (
            <div>
              {
                !cellInfo.row.editing ?
                  <FormattedNumber value={ cellInfo.row.price } style="currency" currency="BRL"/> :
                  <CurrencyInput value={ this.state.newPrice }
                                 className="editingInput"
                                 onKeyPress={(e) => this.onEnterKeyPressed(e)}
                                 onBlur={ (e) => this.handlePriceOnChange(
                                   e, cellInfo.row.partCode, cellInfo.row.comboPartCode
                                 )}
                                 decimalSeparator=","
                                 thousandSeparator="."
                                 autoFocus={true}
                  />
              }
            </div>
          )
        })
    }

    columns.push(
      {
        Header: 'Editing',
        accessor: 'editing',
        className: 'hideTd',
        headerClassName: 'hideTd'
      },
      {
        Header: 'PriceChanged',
        accessor: 'priceChanged',
        className: 'hideTd',
        headerClassName: 'hideTd'
      },
      {
        Header: 'errorToSave',
        accessor: 'errorToSave',
        className: 'hideTd',
        headerClassName: 'hideTd'
      },
      {
        Header: '',
        filterable: false,
        sortable: false,
        headerClassName: 'optionsColumn',
        className: 'optionsColumn',
        Cell: cellInfo => (
          !cellInfo.row.editing ?
            (<div className={this.props.dataRequest === COMBOS && 'editingCombo'}>
              <button onClick={
                            (e) => this.handleEditOnClick(
                              e, cellInfo.row.partCode, cellInfo.row.comboPartCode
                            )
                          }
                  className="editButton"
                  id={cellInfo.row.partCode}
              />
              <OverlayTrigger placement="top" overlay={tooltip}>
                <div style={{ display: cellInfo.row.priceChanged ? 'inline-block' : 'none' }} className="changedLineWarning" />
              </OverlayTrigger>
            </div>)
          :
          <div className= {(this.props.dataRequest === COMBOS && this.state.errorInputValue) ? 'editingComboError' : (this.props.dataRequest === COMBOS && 'editingCombo') } >
              <button onClick={ (e) => this.handlePriceSave(
                                  e, cellInfo.row.partCode, cellInfo.row.comboPartCode
                                )
                              }
                      className="saveButton"
              />
              <button onClick={ (e) => this.handleCancelOnClick(
                                    e, cellInfo.row.partCode, cellInfo.row.comboPartCode
                                  )
                              }
                      className="cancelButton"
              />

              { this.state.errorInputValue && <p>Valor Inválido</p> }
              { cellInfo.row.errorToSave !== undefined && cellInfo.row.errorToSave !== '' && <p>Erro ao salvar</p> }
          </div>
        )
      }
    )


    return (
      this.props.genericData.loadingData !== undefined
       && this.props.genericData.loadingData === true
        ? <h3 className="loadingDiv"> Carregando Dados </h3>
        : this.props.genericData.data
          && this.props.genericData.data.response
          && this.props.genericData.data.response.status !== 200
          ? <div>
              <h3>Erro ao carregar os dados</h3>
              <p> Erro: {this.props.genericData.data.message} </p>
            </div>

          : <div>
            <ReactTable
              data={data}
              columns={columns}
              filterable
              className="productsTable"
              defaultPageSize={rowsToShow}
              minRows = {0}
              defaultSortMethod = { (a, b) => {
                let a1 = a === null || a === undefined ? -Infinity : a
                let b1 = b === null || b === undefined ? -Infinity : b
                a1 = typeof a1 === 'string' ? a1.toLowerCase() : a1
                b1 = typeof b1 === 'string' ? b1.toLowerCase() : b1

                if (typeof a1 === 'string' && a1.indexOf('|') > 0) {
                  a1 = Number(a1.split('|')[0])
                }

                if (typeof b1 === 'string' && b1.indexOf('|') > 0) {
                  b1 = Number(b1.split('|')[0])
                }

                if (a1 > b1) {
                  return 1
                }
                if (a1 < b1) {
                  return -1
                }
                return 0
              }}
              defaultFilterMethod={ (filter, row) => {
                const id = filter.pivotId || filter.id

                if (id.indexOf('price') >= 0) {
                  return row[id] !== undefined ?
                    String(row[id].toFixed(2)).replace(',', '.').indexOf(filter.value.replace(',', '.')) >= 0 :
                    true
                }
                return row[id] !== undefined ?
                    String(row[id]).toLowerCase().replace(',', '.').indexOf(filter.value.toLowerCase().replace(',', '.')) >= 0 :
                    true
              }}
              previousText="Anterior"
              nextText="Próximo"
              loadingText="Carregando..."
              noDataText="Nenhum dado encontrado"
              pageText="Página"
              ofText="de"
              rowsText="linhas"
            />
            <Modal
              className="comboPriceModal"
              show={ this.state.priceComboHigherProduct }
              onHide={ this.handleChangeItemsModalClose.bind(this) }>
              <Modal.Header closeButton>
                <Modal.Title>ATENÇÃO</Modal.Title>
              </Modal.Header>
              <Modal.Body>
                Preço do produto no combo maior do que o preço do produto individual
              </Modal.Body>
              <Modal.Footer>
                <button className="confirmButton" onClick={this.handlePriceSaveModalConfirm.bind(this)}>PROSSEGUIR</button>
                <button onClick={this.handleChangeItemsModalClose.bind(this)}>CANCELAR</button>
              </Modal.Footer>
            </Modal>
          </div>
    )
  }
}

GenericList.propTypes = {
  user: UserPropTypes,
  savingProduct: PropTypes.func,
  savingModifier: PropTypes.func,
  genericData: GenericDataPropTypes,
  editingItem: PropTypes.func,
  cancelEditingItem: PropTypes.func,
  changePriceItem: PropTypes.func,
  dataRequest: PropTypes.string,
  classCode: PropTypes.number,
  productCategory: PropTypes.string,
  onRequestData: PropTypes.func,
  logoutUser: PropTypes.func
}

GenericList.defaultProps = {
  genericData: { data: [], priceChanged: null }
}

const mapStateToProps = state => {
  return {
    genericData: state.generic,
    user: state.user
  }
}

const mapDispatchToProps = dispatch => {
  return {
    onRequestData: (dataRequest, token, productCategory) => dispatch({
      type: GET_ALL_DATA_REQUEST,
      dataRequest: dataRequest,
      token: token,
      productCategory: productCategory
    }),
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
    logoutUser: token => dispatch(logoutUser(token)),
    editingItem: (partCode, comboPartCode) => dispatch(
      editingItem(partCode, comboPartCode)
    ),
    cancelEditingItem: (partCode, comboPartCode) => dispatch(
      cancelEditingItem(partCode, comboPartCode)
    ),
    changePriceItem: (partCode, comboPartCode, newPrice) => dispatch(
      changePriceItem(partCode, comboPartCode, newPrice)
    )
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(GenericList)
