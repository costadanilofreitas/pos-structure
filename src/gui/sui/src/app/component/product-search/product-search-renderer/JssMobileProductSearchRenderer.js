import injectSheet from 'react-jss'

import MobileProductSearchRenderer from './MobileProductSearchRenderer'

const styles = (theme) => ({
  container: {
    height: 'calc(83vh)',
    padding: theme.defaultPadding,
    position: 'fixed',
    zIndex: '3',
    backgroundColor: 'white',
    marginLeft: '-75%',
    width: '100%'
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
    boxSizing: 'border-box',
    height: 'calc(100vh /12)'
  },
  titleWrapper: {
    display: 'flex',
    flexDirection: 'column',
    width: '96%',
    height: '100%',
    padding: '2vh 2%'
  },
  titleBottomCont: {
    flexGrow: 1,
    flexShrink: 0,
    flexBasis: 0,
    marginTop: '1vh',
    position: 'relative'
  },
  productsPanel: {
    position: 'relative',
    margin: '0 2% 2vh',
    backgroundColor: 'white',
    height: '87% !important'
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
  filteredProducts: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    boxSizing: 'border-box'
  },
  filterInput: {
    width: '100%',
    border: '1px solid #e8e5e0',
    boxSizing: 'border-box',
    fontSize: '2vmin',
    padding: '0.5vh 1%',
    outline: 'none'
  }
})

export default injectSheet(styles)(MobileProductSearchRenderer)
