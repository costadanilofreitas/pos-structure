import injectSheet from 'react-jss'
import DefaultMainScreenRenderer from './DefaultMainScreenRenderer'
import TotemMainScreenRenderer from './TotemMainScreenRenderer'

const styles = (theme) => ({
  rootContainer: {
    display: 'flex',
    flexDirection: 'column',
    width: '100%',
    height: '100%',
    background: theme.screenBackground
  },
  bannerContainer: {
    display: 'flex',
    flexDirection: 'column',
    width: '100%',
    height: '100%',
    background: theme.screenBackground
  },
  headerContainer: {
    flex: '2',
    position: 'relative',
    marginTop: '1px'
  },
  contentContainer: {
    flex: '33',
    position: 'relative'
  },
  footerContainer: {
    flex: '1',
    position: 'relative'
  },
  mobileHeaderContainer: {
    flex: '3',
    position: 'relative'
  },
  mobileFooterContainer: {
    flex: '0',
    position: 'relative'
  },
  totemBannerContainer: {
    flex: '5',
    position: 'relative',
    borderBottom: `${theme.defaultPadding} solid ${theme.screenBackground}`,
    boxSizing: 'border-box',
    zIndex: '2'
  },
  totemFooterContainer: {
    flex: '1',
    position: 'relative',
    borderTop: `${theme.defaultPadding} solid ${theme.screenBackground}`,
    boxSizing: 'border-box'
  }
})

const DefaultMainScreen = injectSheet(styles)(DefaultMainScreenRenderer)
const TotemMainScreen = injectSheet(styles)(TotemMainScreenRenderer)

export { DefaultMainScreen, TotemMainScreen }
