import injectSheet from 'react-jss'
import DesktopFooterRenderer from './DesktopFooterRenderer'
import MobileFooterRenderer from './MobileFooterRenderer'
import TotemFooterRenderer from './TotemFooterRenderer'

const styles = (theme) => ({
  footerRoot: {
    composes: 'footer-root',
    position: 'absolute',
    top: '97%',
    height: '3%',
    width: '100%'
  },
  footerVersionTraining: {
    composes: 'footer-version-training',
    color: '#bb0000'
  },
  footerLeftPanel: {
    backgroundColor: theme.footerBackgroundColor || 'white',
    color: theme.fontColor || 'black',
    height: '100%',
    width: '100%',
    fontSize: '1.0vw',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-evenly',
    paddingLeft: theme.defaultPadding,
    ...(theme.footer || {}),
    ...(theme.footerLeftPanel || {})
  },
  footerRightPanel: {
    backgroundColor: theme.footerBackgroundColor || 'white',
    color: theme.fontColor || 'black',
    height: '100%',
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    fontSize: '1.0vw',
    ...(theme.footer || {}),
    ...(theme.footerRightPanel || {})
  },
  periodMismatch: {
    composes: 'footer-period-mismatch',
    color: 'red'
  },
  centerElement: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative !important'
  },
  textElipsis: {
    width: '100%',
    overflow: 'hidden',
    position: 'absolute',
    whiteSpace: 'pre',
    textOverflow: 'ellipsis'
  },
  totemFooter: {
    display: 'flex',
    backgroundColor: theme.footerBackgroundColor,
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    width: '100%',
    height: '100%'
  },
  totemImage: {
    height: '100%',
    width: '90%'
  },
  textCentralize: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    whiteSpace: 'nowrap'
  },
  totemButton: {
    height: '100%',
    width: '10%'
  }
})

const DesktopRenderer = injectSheet(styles)(DesktopFooterRenderer)
const MobileRenderer = injectSheet(styles)(MobileFooterRenderer)
const TotemRenderer = injectSheet(styles)(TotemFooterRenderer)

export { DesktopRenderer, MobileRenderer, TotemRenderer }
