import injectSheet from 'react-jss'
import DesktopOrderTotalRenderer from './DesktopOrderTotalRenderer'

// eslint-disable-next-line no-unused-vars
const styles = (theme) => ({
  divOrderTotal: {
    borderTop: 'solid 1px #7A7577'
  },
  p: {
    borderBottom: 'solid 1px #7A7577',
    borderLeftWidth: '100%',
    position: 'relative',
    marginLeft: '20%',
    borderRadius: '3px'
  }
})

export default injectSheet(styles)(DesktopOrderTotalRenderer)
