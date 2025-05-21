import injectSheet from 'react-jss'
import DesktopRenderer from './DesktopTableActionsRenderer'
import MobileRenderer from './MobileTableActionsRenderer'

// eslint-disable-next-line no-unused-vars
const styles = (theme) => ({
  optionsMenuContainer: {
    position: 'fixed'
  },
  popContainer: {
    width: '100%',
    height: '100%'
  },
  innerPopupContainer: {
    width: '100%',
    height: '100%'
  },
  outerPopUpContainerProgress: {
    width: '100%',
    height: 'calc(100% / 12 * 4)'
  },
  outerPopUpContainerProgressTab: {
    width: '100%',
    height: 'calc(100% / 12 * 2)'
  },
  outerPopUpContainerTotaled: {
    width: '100%',
    height: 'calc(100% / 12 * 1)'
  }
})

const mobile = injectSheet(styles)(MobileRenderer)
const desktop = injectSheet(styles)(DesktopRenderer)

export { desktop as DesktopTableActionsRenderer, mobile as MobileTableActionRenderer }
