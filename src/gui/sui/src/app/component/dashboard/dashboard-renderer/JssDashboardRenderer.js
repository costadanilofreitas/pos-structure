import injectSheet from 'react-jss'
import DesktopDashboardRenderer from './DesktopDashboardRenderer'

// eslint-disable-next-line no-unused-vars
const styles = (theme) => ({
  absoluteWrapper: {
    width: '100%',
    height: '100%',
    position: 'absolute'
  }
})

export default injectSheet(styles)(DesktopDashboardRenderer)
