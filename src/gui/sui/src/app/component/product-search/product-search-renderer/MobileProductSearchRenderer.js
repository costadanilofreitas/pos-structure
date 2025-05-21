import React, { Component } from 'react'
import _ from 'lodash'
import { I18N, MessageBus } from '3s-posui/core'
import PropTypes from 'prop-types'
import { ScrollTable, Column } from '3s-widgets'


export default class MobileProductSearchRenderer extends Component {
  constructor(props) {
    super(props)
    this.msgBus = new MessageBus(this.props.posId)
    this.columns = [
      {
        path: 'product_code',
        title: <I18N id="$PLU" defaultMessage="PLU"/>
      },
      {
        path: 'name',
        title: <I18N id="$PRODUCT_NAME" defaultMessage="Product Name"/>
      },
      {
        path: null,
        title: <I18N id="$ACTION" defaultMessage="Action"/>,
        onRenderCell: this.props.actionRenderer
      }
    ]
    this.columns = [
      <Column
        key={1}
        width={100}
        label="PLU"
        dataKey="product_code"
      />,
      <Column
        key={2}
        width={500}
        label="Nome do Produto"
        dataKey="name"
      />,
      <Column
        key={3}
        width={100}
        label="Ação"
        dataKey="action"
        cellRenderer={ this.props.actionRenderer }
      />
    ]

    this.debouncedSearch = _.debounce(this.props.handleSearch, 500)
    this.state = {
      removeFocus: false
    }
    this.handleOnKeyPress = this.handleOnKeyPress.bind(this)
  }

  handleOnKeyPress(event) {
    if (event.key === 'Enter') {
      this.buttonDOM.blur()
    }
  }

  render() {
    const { classes, filteredProducts } = this.props

    return (
      <div className={classes.container}>
        <div className={classes.titlePanel}>
          <div className={classes.titleWrapper}>
            <div className={classes.titleBottomCont}>
              <input
                autoFocus
                ref={(buttonDOM) => {
                  this.buttonDOM = buttonDOM
                }}
                onKeyPress={this.handleOnKeyPress}
                className={classes.filterInput}
                onChange={(evt) => this.debouncedSearch(evt.target.value)}
                placeholder="Comece a digitar o nome do produto que deseja procurar"
              />
            </div>
          </div>
        </div>
        <div className={classes.productsPanel}>
          <div className={classes.absoluteWrapper}>
            <div className={classes.productsCont}>
              <div className={classes.filteredProducts}>
                <ScrollTable
                  data={filteredProducts}
                  columns={this.columns}
                  rowsQuantity={10}
                  tableFlex={10}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }
}

MobileProductSearchRenderer.propTypes = {
  classes: PropTypes.object,
  posId: PropTypes.number,
  actionRenderer: PropTypes.func,
  handleSearch: PropTypes.func,
  filteredProducts: PropTypes.array
}
