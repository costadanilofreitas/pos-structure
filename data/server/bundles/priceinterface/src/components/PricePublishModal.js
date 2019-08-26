import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Modal } from 'react-bootstrap'
import GenericProduct from './GenericProduct'

class PricePublishModal extends Component {
  constructor(props) {
    super(props)
    this.state = {
      showProducts: this.props.showProducts,
      showCombos: this.props.showCombos,
      showModifiers: this.props.showModifiers,
      productType: '',
      showChangeItemsModal: false,
      productCategory: this.props.productCategory
    }

    this.handleChangeItemsModalClose = this.handleChangeItemsModalClose.bind(this)
    this.handleChangeItemsModalShow = this.handleChangeItemsModalShow.bind(this)
    this.handleTableProductsShow = this.handleTableProductsShow.bind(this)
    this.handleTableCombosShow = this.handleTableCombosShow.bind(this)
    this.handleTableModifiersShow = this.handleTableModifiersShow.bind(this)
  }

  componentWillReceiveProps(nextProps) {
    this.setState({
      showChangeItemsModal: nextProps.showModal,
      showProducts: nextProps.showProducts,
      showModifiers: nextProps.showModifiers,
      showCombos: nextProps.showCombos,
      productCategory: nextProps.productCategory
    })
  }

  render() {
    return (
      <Modal
        className="changedPriceModal"
        show={this.state.showChangeItemsModal}
        onHide={ this.handleChangeItemsModalClose.bind(this) }>
        <Modal.Header closeButton>
          <Modal.Title>Resumo das alterações</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <div className="changedPriceOptions">
            {(this.props.changedItems &&
              this.props.changedItems.products &&
              this.props.changedItems.products.length > 0) &&
            this.props.changedItems.products.filter(prod => prod.category === 'sandwich').length > 0 &&
            <div>
              <button
                className={this.state.showProducts && this.state.productCategory === 'sandwich' && 'active'}
                onClick={ this.handleTableProductsShow.bind(this, 'sandwich') }>
                Sanduíches
              </button>
            </div>
            }
            {(this.props.changedItems &&
              this.props.changedItems.products &&
              this.props.changedItems.products.length > 0) &&
            this.props.changedItems.products.filter(prod => prod.category === 'accompaniment').length > 0 &&
            <div>
              <button
                className={this.state.showProducts && this.state.productCategory === 'accompaniment' && 'active'}
                onClick={ this.handleTableProductsShow.bind(this, 'accompaniment') }>
                Acompanhamentos
              </button>
            </div>
            }
            {(this.props.changedItems &&
              this.props.changedItems.products &&
              this.props.changedItems.products.length > 0) &&
            this.props.changedItems.products.filter(prod => prod.category === 'beverage').length > 0 &&
            <div>
              <button
                className={this.state.showProducts && this.state.productCategory === 'beverage' && 'active'}
                onClick={ this.handleTableProductsShow.bind(this, 'beverage') }>
                Bebidas
              </button>
            </div>
            }
            {(this.props.changedItems &&
              this.props.changedItems.products &&
              this.props.changedItems.products.length > 0) &&
            this.props.changedItems.products.filter(prod => prod.category === 'desert').length > 0 &&
            <div>
              <button
                className={this.state.showProducts && this.state.productCategory === 'desert' && 'active'}
                onClick={ this.handleTableProductsShow.bind(this, 'desert') }>
                Sobremesas
              </button>
            </div>
            }
            {(this.props.changedItems &&
              this.props.changedItems.combos &&
              this.props.changedItems.combos.length > 0) &&
            <div>
              <button
                className={this.state.showCombos && 'active'}
                onClick={this.handleTableCombosShow.bind(this)}>
                Combos
              </button>
            </div>
            }
            {(this.props.changedItems &&
              this.props.changedItems.modifiers &&
              this.props.changedItems.modifiers.length > 0) &&
            <div>
              <button
                className={this.state.showModifiers && 'active'}
                onClick={this.handleTableModifiersShow.bind(this)}>
                Adicionais
              </button>
            </div>
            }
          </div>
          <table className="table">
            <thead>
            <tr className="headerTable">
              { this.state.showCombos &&
              <th className="codeProductHeader">Código Combo</th>
              }
              <th className="codeProductHeader">Código Produto</th>
              <th className="nameProductHeader">Nome</th>
              { this.state.showCombos &&
              <th className="priceProductHeader">Preço Individual</th>
              }
              { this.state.showCombos &&
              <th className="priceProductHeader">Preço no Combo</th>
              }
              { !this.state.showCombos &&
              <th className="priceProductHeader">Preço</th>
              }
            </tr>

            </thead>
            <tbody>
            { this.state.showProducts &&
            this.props.changedItems &&
            this.props.changedItems.products &&
            this.props.changedItems.products.filter(
              prod => prod.category === this.state.productCategory
            ).map((product, i) =>
              <GenericProduct
                key={ i + '_' + product.partCode }
                product={ product }
                dataRequest={ 'PRODUCTS' }
                hideEdit={true}
              />)
            }
            { this.state.showCombos &&
            this.props.changedItems &&
            this.props.changedItems.combos &&
            this.props.changedItems.combos.map((combo, i) =>
              <GenericProduct
                key={ i + '_' + combo.comboPartCode }
                product={ combo }
                dataRequest={ 'COMBOS' }
                hideEdit={true}
              />)
            }
            { this.state.showModifiers &&
            this.props.changedItems &&
            this.props.changedItems.modifiers &&
            this.props.changedItems.modifiers.map((modifier, i) =>
              <GenericProduct
                key={ i + '_' + modifier.partCode }
                product={ modifier }
                dataRequest={ 'MODIFIERS' }
                hideEdit={true}
              />)
            }
            </tbody>
          </table>
        </Modal.Body>
      </Modal>
    )
  }

  handleChangeItemsModalClose() {
    this.setState({ showChangeItemsModal: false })
  }

  handleChangeItemsModalShow() {
    this.setState({ showChangeItemsModal: true })
  }

  handleTableProductsShow(category) {
    this.setState({
      showProducts: true,
      showCombos: false,
      showModifiers: false,
      productCategory: category
    })
  }

  handleTableCombosShow() {
    this.setState({
      showProducts: false,
      showCombos: true,
      showModifiers: false
    })
  }

  handleTableModifiersShow() {
    this.setState({
      showProducts: false,
      showCombos: false,
      showModifiers: true
    })
  }
}

PricePublishModal.propTypes = {
  changedItems: PropTypes.object,
  showModal: PropTypes.bool,
  showProducts: PropTypes.bool,
  showCombos: PropTypes.bool,
  showModifiers: PropTypes.bool,
  productCategory: PropTypes.string
}

export default PricePublishModal
