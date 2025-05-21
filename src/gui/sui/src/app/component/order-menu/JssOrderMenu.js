import injectSheet from 'react-jss'
import OrderMenu from './OrderMenu'

const styles = (theme) => ({
  submenu: {
    backgroundColor: theme.backgroundColor,
    color: theme.fontColor,
    fontSize: '1.1vh !important',
    borderBottom: '5px solid #DCDDDE !important'
  },
  submenuActive: {
    backgroundColor: theme.backgroundColor,
    color: theme.fontColor,
    fontSize: '1.3vh !important',
    fontWeight: 'bold',
    borderBottom: '5px solid #002051 !important'
  },
  submenuNotLast: {
    ...(theme.submenuNotLast || {})
  },
  tabButtonStyle: {
    flexGrow: 1,
    flexShrink: 0,
    flexBasis: 0,
    padding: '1px'
  }
})

export default injectSheet(styles)(OrderMenu)
