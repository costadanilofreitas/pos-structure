import injectSheet from 'react-jss'

import MobileQtyButtonsRenderer from './MobileQtyButtonsRenderer'

const styles = (theme) => ({
  qtyCont: {
    display: 'flex',
    flexDirection: 'column',
    width: '100%',
    height: '100%',
    position: 'absolute'
  },
  qtyTitle: {
    flexGrow: 20,
    flexShrink: 0,
    flexBasis: 0,
    backgroundColor: theme.backgroundColor,
    fontSize: '2vmin',
    padding: '0.5vmin 0',
    textAlign: 'center',
    position: 'relative'
  },
  qtyButton: {
    color: theme.fontColor,
    backgroundColor: '#FFFFFF !important',
    fontSize: '3.8vmin !important'
  },
  qtyGridCont: {
    position: 'relative',
    flexGrow: 80,
    flexShrink: 0,
    flexBasis: 0
  },
  qtyGridPadding: {
    boxSizing: 'border-box',
    '& .button-grid-cell-root': {
    }
  },
  container: {
    width: '100%',
    height: `calc(100% - ${theme.defaultPadding})`,
    padding: `${theme.defaultPadding} 0 0 0`
  }
})

export default injectSheet(styles)(MobileQtyButtonsRenderer)
