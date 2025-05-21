import { injectMultipleSheet } from '../../../../../util/reactJssUtil'
import DesktopRenderer from './DesktopTableOrderDetails'
import MobileRenderer from './MobileTableOrderDetails'

// eslint-disable-next-line no-unused-vars
const commonStyles = (theme) => ({
  salePanelContainer: {
    border: '0px !important',
    position: 'absolute',
    height: '100%',
    width: '100%'
  },
  salePanelOuterContainer: {
    height: '100%'
  },
  orderHeader: {
    borderBottom: '1px solid #ccc'
  }
})

const mobileStyles = (theme) => ({
  rootContainer: {
    width: '100%',
    height: 'calc((100% - 1.0vw) / 8)'
  },
  rootContainerWithDetails: {
    width: '100%',
    height: 'calc(((100% - 1.0vw) / 8) * 5)'
  },
  orderContainer: {
    margin: `calc( ${theme.defaultPadding} /2)`,
    width: `calc(100% - ${theme.defaultPadding})`,
    height: `calc(100% - ${theme.defaultPadding})`
  },
  orderContainerWithDetails: {
    height: '20%'
  },
  salePanelContainer: {
    height: '80%',
    width: '100%'
  }
})

const desktopStyles = (theme) => ({
  orderContainer: {
    margin: `calc( ${theme.defaultPadding} /2)`,
    width: `calc((100% / 3) - ${theme.defaultPadding})`,
    height: `calc((100% / 2) - ${theme.defaultPadding})`,
    float: 'left'
  }
})

const mobile = injectMultipleSheet(commonStyles, mobileStyles)(MobileRenderer)
const desktop = injectMultipleSheet(commonStyles, desktopStyles)(DesktopRenderer)

export { mobile as MobileTableOrderDetails, desktop as DesktopTableOrderDetails }
