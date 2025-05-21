import injectSheet from 'react-jss'

import QtyButtons from './QtyButtons'

const styles = (theme) => ({
  qtyCont: {
    display: 'flex',
    flexDirection: 'column',
    width: '100%',
    height: '100%',
    position: 'absolute'
  },
  qtyTitle: {
    flexGrow: 1,
    flexShrink: 0,
    flexBasis: 0,
    color: '#888888',
    backgroundColor: theme.backgroundColor,
    fontSize: '1vmin',
    padding: '2vmin 0',
    textAlign: 'center'
  },
  qtyButton: {
    color: theme.fontColor,
    backgroundColor: theme.backgroundColor,
    fontSize: '3.8vmin !important'
  },
  qtyGridCont: {
    position: 'relative',
    flexGrow: 99,
    flexShrink: 0,
    flexBasis: 0
  },
  qtyGridPadding: {
    boxSizing: 'border-box',
    '& .button-grid-cell-root': {
    }
  }
})

export default injectSheet(styles)(QtyButtons)
