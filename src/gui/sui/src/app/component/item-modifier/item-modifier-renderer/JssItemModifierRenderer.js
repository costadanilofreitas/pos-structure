import injectSheet from 'react-jss'
import ItemModifierRenderer from './ItemModifierRenderer'

const styles = (theme) => ({
  container: {
    backgroundColor: theme.backgroundColor,
    height: `calc(100% - (${theme.defaultPadding} / 2)) !important`,
    borderTop: `calc(${theme.defaultPadding} / 2) solid ${theme.screenBackground}`
  },
  centeredDiv: {
    display: 'flex',
    height: '100%',
    width: '100%',
    justifyContent: 'center',
    alignItems: 'center'
  },
  titleContainer: {
    height: '100%',
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: theme.titleBackgroundColor
  },
  selectionDropBox: {
    height: '100%',
    width: '100%'
  },
  tabs: {
    height: '100%',
    width: '100%'
  },
  tabItem: {
    display: 'flex',
    flexDirection: 'column',
    width: `calc(100% - ${theme.defaultPadding})`,
    height: `calc(100% - ${theme.defaultPadding})`,
    margin: `calc(${theme.defaultPadding} / 2)`,
    color: theme.fontColor,
    backgroundColor: `${theme.titleBackgroundColor} !important`
  },
  tabItemSelected: {
    fontWeight: 'bold',
    border: `1px solid ${theme.pressedBackgroundColor}`,
    borderBottom: `10px solid ${theme.pressedBackgroundColor}`,
    backgroundColor: `${theme.backgroundColor} !important`,
    color: `${theme.fontColor} !important`
  },
  productItem: {
    position: 'absolute',
    fontSize: '1.2vmin !important',
    height: `calc(100% - ${theme.defaultPadding})`,
    width: `calc(100% - ${theme.defaultPadding})`,
    margin: `calc(${theme.defaultPadding} / 2)`,
    backgroundColor: theme.productBackgroundColor,
    color: theme.productColor
  },
  productItemSelected: {
    fontSize: '1.3vh !important',
    height: `calc(100% - ${theme.defaultPadding})`,
    borderBottom: `10px solid ${theme.pressedBackgroundColor}`,
    fontWeight: 'bold'
  },
  itemQuantity: {
    top: '0.3vh',
    right: `calc(0.3vh + ${theme.defaultPadding})`,
    position: 'absolute',
    fontSize: '2.5vmin !important'
  }
})

export default injectSheet(styles)(ItemModifierRenderer)
