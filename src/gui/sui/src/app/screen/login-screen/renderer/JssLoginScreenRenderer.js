import injectSheet from 'react-jss'

import MobileLoginScreenRenderer from './MobileLoginScreenRenderer'
import DesktopLoginScreenRenderer from './DesktopLoginScreenRenderer'

const styles = (theme) => ({
  mobileRootContainer: {
    display: 'flex',
    flexDirection: 'column',
    width: '100%',
    height: '100%'
  },
  desktopRootContainer: {
    display: 'flex',
    flexDirection: 'row',
    width: '100%',
    height: '100%'
  },
  infoContainer: {
    flexGrow: '3',
    display: 'flex',
    position: 'relative',
    margin: `calc(${theme.defaultPadding}/ 2)`
  },
  mobileLogoContainer: {
    flexGrow: '1',
    position: 'relative',
    margin: `calc(${theme.defaultPadding}/ 2)`,
    background: theme.loginScreenBackgroundColor
  },
  desktopLogoContainer: {
    flexGrow: '3',
    position: 'relative',
    marginBottom: theme.defaultPadding,
    background: theme.loginScreenBackgroundColor
  },
  loginInfoContainer: {
    flexGrow: '1',
    position: 'relative',
    margin: `calc(${theme.defaultPadding}/ 2)`,
    background: theme.loginScreenBackgroundColor
  },
  numpadContainer: {
    flexGrow: '8',
    position: 'relative',
    background: theme.loginScreenBackgroundColor
  },
  dashboardContainer: {
    flexGrow: '2',
    display: 'flex',
    position: 'relative',
    margin: theme.defaultPadding,
    background: theme.loginScreenBackgroundColor
  },
  loginContainer: {
    flexGrow: '1',
    position: 'relative'
  },
  loginInnerContainer: {
    display: 'flex',
    flexDirection: 'column'
  }
})

const MobileRenderer = injectSheet(styles)(MobileLoginScreenRenderer)
const DesktopRenderer = injectSheet(styles)(DesktopLoginScreenRenderer)

export { MobileRenderer, DesktopRenderer }
