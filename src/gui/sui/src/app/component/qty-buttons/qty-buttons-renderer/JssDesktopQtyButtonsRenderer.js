import injectSheet from 'react-jss'

import DesktopQtyButtonsRenderer from './DesktopQtyButtonsRenderer'

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
    backgroundColor: theme.qtyButtonColor,
    fontSize: '1vmin',
    padding: '2vh 0',
    textAlign: 'center',
    fontWeight: 'bold'
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
      '&:not(:last-child)': {
        borderBottom: 'solid 1px #dadada'
      }
    }
  },
  qtyButton: {
    color: theme.fontColor,
    fontSize: '3.8vh !important'
  },
  qtyButtonSelected: {
    backgroundColor: theme.pressedBackgroundColor,
    textShadow: 'none',
    color: theme.pressedColor
  },
  qtyButtonUnselected: {
    backgroundColor: theme.qtyButtonColor
  }
})

export default injectSheet(styles)(DesktopQtyButtonsRenderer)
