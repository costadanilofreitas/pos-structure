import injectSheet from 'react-jss'
import Renderer from './HeaderRenderer'

const styles = (theme) => ({
  menuItemsContainer: {
    position: 'absolute',
    display: 'flex',
    height: '100%',
    width: '100%',
    '& > div:first-child': {
      paddingLeft: '1px'
    },
    '& > div:last-child': {
      paddingRight: '1px'
    }
  },
  menuItem: {
    fontSize: '0.4em',
    height: '100%',
    flex: '1',
    paddingLeft: '1px'
  },
  optionsMenuContainer: {
    position: 'fixed'
  },
  popContainer: {
    width: '100%',
    height: '100%'
  },
  innerPopupContainer: {
    width: '100%',
    height: '200%'
  },
  numberCircle: {
    borderRadius: '50%',
    width: '0.8vmin !important',
    height: '0.8vmin',
    padding: '0.5vh',
    background: theme.recallNotificationColor,
    color: theme.activeColor,
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'absolute',
    top: '2vmin',
    right: '0'
  },
  chatCircle: {
    borderRadius: '50%',
    width: '0.8vmin !important',
    height: '0.8vmin',
    padding: '0.5vh',
    background: theme.chatNotificationColor,
    color: theme.activeColor,
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'absolute',
    top: '2vmin',
    right: '0'
  },
  icon: {
    top: '0.5vmin',
    right: '1vmin',
    position: 'absolute',
    fontSize: '2.5vmin',
    color: theme.recallIconColor
  },
  disabledColor: {
    color: theme.disabledColor
  },
  disabledBackgroundColor: {
    background: theme.disabledColor
  }
})

export default injectSheet(styles)(Renderer)
