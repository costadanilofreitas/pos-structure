import injectSheet from 'react-jss'
import MobileOrderScreenRenderer from './renderer/MobileOrderScreenRenderer'
import DesktopOrderScreenRenderer from './renderer/DesktopOrderScreenRenderer'
import TotemOrderScreenRenderer from './renderer/TotemOrderScreenRenderer'


const styles = (theme) => ({
  container: {
    width: '100%',
    height: `calc(100% - ${theme.defaultPadding})`,
    padding: `${theme.defaultPadding} 0 0 0`
  },
  quantityContainer: {
    margin: `0 0 0 ${theme.defaultPadding}`,
    backgroundColor: theme.backgroundColor
  },
  saleItemsContainer: {
    margin: theme.defaultPadding,
    backgroundColor: theme.backgroundColor
  },
  saleItemsContainerMobile: {
    backgroundColor: theme.backgroundColor
  },
  menuTabsContainer: {
    height: `calc(100% - ${theme.defaultPadding})`
  },
  totemProductsContainer: {
    border: `${theme.defaultPadding} solid ${theme.screenBackground}`,
    boxSizing: 'border-box',
    overflow: 'auto'
  },
  tabButtonStyle: {
    flexGrow: 1,
    flexShrink: 0,
    flexBasis: 0,
    padding: '1px'
  },
  submenu: {
    backgroundColor: 'white',
    color: 'black',
    fontSize: '1.1vh !important',
    borderBottom: 'none !important'
  }
})


const MobileRenderer = injectSheet(styles)(MobileOrderScreenRenderer)
const DesktopRenderer = injectSheet(styles)(DesktopOrderScreenRenderer)
const TotemRenderer = injectSheet(styles)(TotemOrderScreenRenderer)

export { MobileRenderer, DesktopRenderer, TotemRenderer }
