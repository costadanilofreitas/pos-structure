import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import _ from 'lodash'
import { MessageBus, I18N } from 'posui/core'
import { Button } from 'posui/button'
import { ScrollPanel, DataTable } from 'posui/widgets'
import injectSheet, { jss } from 'react-jss'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = (theme) => ({
  container: {
    position: 'absolute',
    display: 'flex',
    flexDirection: 'column',
    width: '100%',
    height: '100%'
  },
  absoluteWrapper: {
    position: 'absolute',
    width: '100%',
    height: '100%'
  },
  titlePanel: {
    flexGrow: 1,
    flexShrink: 0,
    flexBasis: 0,
    position: 'relative',
    boxSizing: 'border-box'
  },
  titleWrapper: {
    display: 'flex',
    flexDirection: 'column',
    width: '96%',
    height: '100%',
    padding: '2vh 2%'
  },
  titleTopCont: {
    flexGrow: 1,
    flexShrink: 0,
    flexBasis: 0,
    position: 'relative'
  },
  titleBottomCont: {
    flexGrow: 1,
    flexShrink: 0,
    flexBasis: 0,
    marginTop: '1vh',
    position: 'relative'
  },
  title: {
    fontSize: '2.5vh',
    color: theme.color,
    textTransform: 'uppercase',
    position: 'relative',
    float: 'left'
  },
  priceLookup: {
    backgroundColor: '#b9663d',
    color: 'white',
    position: 'relative',
    float: 'right',
    width: 'auto !important'
  },
  productsPanel: {
    position: 'relative',
    flexGrow: 99,
    flexShrink: 0,
    flexBasis: 0,
    margin: '0 2% 2vh'
  },
  productsCont: {
    position: 'relative',
    color: '#000000',
    textAlign: 'center',
    whiteSpace: 'pre',
    width: '100%',
    height: '100%',
    border: '1px solid #e8e5e0',
    boxSizing: 'border-box'
  },
  products: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    boxSizing: 'border-box'
  },
  loadingSpinner: {
    composes: 'fa fa-spinner fa-spin fa-4x loading-screen-spinner',
    color: '#777777',
    width: '64px',
    height: '64px',
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
    margin: 'auto',
    maxWidth: '100%',
    maxHeight: '100%',
    overflow: 'hidden',
    position: 'relative',
    marginTop: '30vh'
  },
  barCodeIcon: {
    padding: '1vh 1vh 0.5vh'
  },
  dataTable: {
    '& tr td:first-child': {
      paddingLeft: '1%',
      textAlign: 'right'
    },
    '& tr td:last-child': {
      paddingRight: '1%'
    },
    '& tr td:nth-child(2)': {
      textAlign: 'right'
    },
    '& tr td:nth-child(3)': {
      paddingLeft: '1%',
      textAlign: 'left'
    },
    '& tr td:nth-child(4)': {
      paddingRight: '1%',
      textAlign: 'right'
    }
  },
  filterInput: {
    width: '100%',
    border: '1px solid #e8e5e0',
    boxSizing: 'border-box',
    fontSize: '2vh',
    padding: '0.5vh 1%',
    outline: 'none'
  }
})

class ProductSearch extends PureComponent {

  constructor(props) {
    super(props)
    this.msgBus = new MessageBus(this.props.posId)
    this.columns = [
      {
        path: 'barcode',
        title: <I18N id="$BAR_CODE" defaultMessage="Bar Code" />
      },
      {
        path: 'plu',
        title: <I18N id="$PLU" defaultMessage="PLU" />
      },
      {
        path: 'name',
        title: <I18N id="$PRODUCT_NAME" defaultMessage="Product Name" />
      },
      {
        path: 'price',
        title: <I18N id="$PRICE" defaultMessage="Price" />
      },
      {
        path: null,
        title: <I18N id="$ACTION" defaultMessage="Action" />,
        onRenderCell: this.actionRenderer
      }
    ]
    this.debouncedSearch = _.debounce(this.handleSearch, 500)
  }

  state = {
    products: [],
    filter: ''
  }

  actionRenderer = (line) => {
    const { onSellItem } = this.props
    return (
      <Button
        rounded={true}
        style={{ backgroundColor: '#b9663d', color: 'white', height: '4vh' }}
        executeAction={() => onSellItem(line)}
        text="$SELL"
        defaultText="Sell"
      />
    )
  }

  handleSearch = (filter) => {
    const { fullProductList } = this.props
    const filteredData = ProductSearch.filterData(fullProductList || [], { ...this.state, filter: filter || '' })
    this.setState({
      filter,
      products: filteredData
    })
  }

  static filterData = (data, state) => {
    const { filter } = state
    const searchFields = ['barcode', 'plu', 'name']
    const filterStr = filter.toString()
    const filterLower = filterStr.toLowerCase()

    if (filterStr.length === 0) {
      // no filter selected, return everything
      return data
    }
    let dataFiltered = _.filter(data, (obj) => {
      return _.some(searchFields, key => {
        const value = _.get(obj, key)
        return (
          value &&
          filter !== '' &&
          value.toString().toLowerCase().indexOf(filterLower) !== -1
        )
      })
    })
    return dataFiltered
  }

  render() {
    const { classes, fullProductList } = this.props
    const { products } = this.state
    const loading = (fullProductList === null)
    const hasProducts = (products || []).length > 0

    return (
      <div className={classes.container}>
        <div className={classes.titlePanel}>
          <div className={classes.titleWrapper}>
            <div className={classes.titleTopCont}>
              <div className={classes.title}><I18N id="$PRODUCT_SEARCH" defaultMessage="Product Search" /></div>
              <Button className={classes.priceLookup} executeAction={['doPriceLookup']} rounded={true}>
                <i className={`${classes.barCodeIcon} fa fa-barcode fa-2x`} aria-hidden="true"></i>
                <I18N id="$PRICE_LOOKUP" defaultMessage="Price Lookup" />
              </Button>
            </div>
            <div className={classes.titleBottomCont}>
              <input
                autoFocus
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
              <div className={classes.products}>
                {loading && <div className={classes.loadingSpinner} />}
                {(!loading && hasProducts) &&
                  <ScrollPanel styleCont={{ fontWeight: 'normal' }}>
                    <DataTable
                      className={classes.dataTable}
                      style={{ borderCollapse: 'collapse' }}
                      styleHeaderRow={{ height: '7vh' }}
                      styleRow={{ height: '7vh', borderTop: '1px solid #cccccc' }}
                      columns={this.columns}
                      data={products}
                    />
                  </ScrollPanel>
                }
                {(!loading && !hasProducts) &&
                  <div><I18N id="$NO_PRODUCTS_FOUND" defaultMessage="No products found!" /></div>
                }
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }
}

ProductSearch.propTypes = {
  /**
   * Injected classes
   * @ignore
   */
  classes: PropTypes.object,
  /**
   * POS id from `posIdReducer` app state
   * @ignore
   */
  posId: PropTypes.number,
  /**
   * Function called to sell a product
   */
  onSellItem: PropTypes.func,
  /**
   * List of products retrieved from saga
   */
  fullProductList: PropTypes.array
}


function mapStateToProps({ posId, products }) {
  return {
    posId,
    fullProductList: products
  }
}

export default connect(mapStateToProps)(injectSheet(styles)(ProductSearch))

