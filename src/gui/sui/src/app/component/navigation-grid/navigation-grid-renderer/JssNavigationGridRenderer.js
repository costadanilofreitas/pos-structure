import injectSheet from 'react-jss'
import DesktopNavigationGridRenderer from './DesktopNavigationGridRenderer'
import TotemNavigationGridRenderer from './TotemNavigationGridRenderer'

const styles = (theme) => ({
  navigationGridFlexCont: {
    composes: 'navigation-grid-flex-cont',
    display: 'flex',
    flexDirection: 'row',
    height: '100%',
    borderTop: `${theme.defaultPadding} solid ${theme.screenBackground}`,
    boxSizing: 'border-box'
  },
  navigationGridPadding: {
    composes: 'navigation-grid-padding',
    boxSizing: 'border-box'
  },
  navigationGridBoxCont: {
    composes: 'navigation-grid-box-cont',
    width: '100%',
    height: '100%',
    position: 'relative'
  },
  navigationGridBox: {
    composes: 'navigation-grid-box'
  },
  totemTitle: {
    color: theme.titleBackgroundColor,
    fontSize: '2vmin'
  }
})

const DesktopRenderer = injectSheet(styles)(DesktopNavigationGridRenderer)
const MobileRenderer = injectSheet(styles)(DesktopNavigationGridRenderer)
const TotemRenderer = injectSheet(styles)(TotemNavigationGridRenderer)

export { DesktopRenderer, MobileRenderer, TotemRenderer }
