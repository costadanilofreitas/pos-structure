import injectSheet from 'react-jss'

import ProductGrid from './ProductGrid'

// eslint-disable-next-line no-unused-vars
const styles = (theme) => ({
  navigationButton: {
    fontSize: '1.1vh !important'
  },
  productText: {
    height: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'column'
  },
  productTextWithImage: {
    right: '0',
    color: 'white',
    fontWeight: 'bold',
    textShadow: '-1px 0 black, 0 1px black, 1px 0 black, 0 -1px black'
  }
})

export default injectSheet(styles)(ProductGrid)
