import DesktopTableDetailsRenderer from './DesktopTableDetailsRenderer'
import MobileTableDetailsRenderer from './MobileTableDetailsRenderer'
import TotemTableDetailsRenderer from './TotemTableDetailsRenderer'
import { injectMultipleSheet } from '../../../../util/reactJssUtil'


// eslint-disable-next-line no-unused-vars
const desktopStyles = (theme) => ({
})

const mobileStyles = (theme) => ({
  container: {
    height: '100%',
    width: '100%',
    backgroundColor: theme.backgroundColor
  },
  collapseIcon: {
    float: 'right',
    minWidth: '40px',
    marginRight: theme.defaultPadding
  },
  popUpContainer: {
    width: '100%',
    height: 'calc(100% / 12 * 4)',
    position: 'fixed',
    left: '0'
  },
  tableInfoFaIcon: {
    textAlign: 'center',
    minWidth: '40px'
  }
})

const commonStyles = (theme) => (
  {
    tableInfoBox: {
      height: '100%',
      width: '100%',
      backgroundColor: theme.backgroundColor
    },
    titleContainer: {
      height: '100%',
      width: '100%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: theme.dialogTitleBackgroundColor,
      color: '#FFF'
    },
    detailsTitle: {
      fontSize: '3vmin',
      fontWeight: 'bold',
      textAlign: 'center',
      margin: '0',
      width: '100%',
      padding: theme.defaultPadding
    },
    tableInfo: {
      fontSize: '1.8vmin',
      display: 'flex',
      flexDirection: 'column',
      paddingTop: '0.2vh',
      backgroundColor: theme.backgroundColor,
      width: '100%',
      height: `calc(100% - ${theme.defaultPadding})`
    },
    tableInfoItems: {
      display: 'flex',
      flex: '1'
    },
    tableInfoItemsLeft: {
      flex: '1',
      margin: '0',
      fontWeight: 'bold'
    },
    tableInfoRight: {
      flex: '1',
      margin: '0'
    },
    tableInfoFaIcon: {
      height: '1.2vw',
      textAlign: 'center',
      minWidth: '40px'
    },
    labelInfo: {
      textOverflow: 'ellipsis',
      overflow: 'hidden',
      whiteSpace: 'pre',
      position: 'absolute',
      width: '100%'
    },
    alignFlexItems: {
      display: 'flex',
      alignItems: 'center'
    }
  }
)

const desktop = injectMultipleSheet(commonStyles, desktopStyles)(DesktopTableDetailsRenderer)
const mobile = injectMultipleSheet(commonStyles, mobileStyles)(MobileTableDetailsRenderer)
const totem = injectMultipleSheet(commonStyles, mobileStyles)(TotemTableDetailsRenderer)
export { desktop as DesktopRenderer, mobile as MobileRenderer, totem as TotemRenderer }
