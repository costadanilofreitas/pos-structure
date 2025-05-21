import injectSheet from 'react-jss'
import BlockDialogRenderer from './BlockDialogRenderer'

const styles = (theme) => ({
  container: {
    backgroundColor: theme.modalOverlayBackground,
    top: 0,
    left: 0,
    height: '100%',
    width: '100%',
    zIndex: '1000',
    position: 'absolute',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center'
  },
  loadingIcon: {
    fontSize: '20vh !important',
    color: 'white',
    animation: 'fa-spin 2s infinite linear',
    WebkitAnimation: 'fa-spin 2s infinite linear'
  }
})

export default injectSheet(styles)(BlockDialogRenderer)
