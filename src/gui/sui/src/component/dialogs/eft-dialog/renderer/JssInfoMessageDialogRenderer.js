import injectSheet from 'react-jss'
import InfoMessageDialogRenderer from './InfoMessageDialogRenderer'

// eslint-disable-next-line no-unused-vars
const styles = (theme) => ({
  clickArea: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    top: 0,
    zIndex: 1000
  },
  messageClassName: {
    fontSize: '5vmin'
  }
})

export default injectSheet(styles)(InfoMessageDialogRenderer)
