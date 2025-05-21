import { connect } from 'react-redux'
import injectSheet from 'react-jss'

import MobileTableListScreenRenderer from './MobileTableListScreenRenderer'
import DesktopTableListScreenRenderer from './DesktopTableListScreenRenderer'

const styles = (theme) => ({
  absoluteWrapper: {
    position: 'absolute',
    width: '100%',
    height: '100%'
  },
  tableListBackground: {
    width: '100%',
    height: '100%',
    backgroundColor: theme.tableScreenBackgroundColor
  },
  titleContainer: {
    fontSize: '1.8vmin',
    fontWeight: 'bold',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.backgroundColor
  },
  goalsContainer: {
    width: `calc(100% - 2 * ${theme.defaultPadding})`,
    height: `calc(100% - 2 * ${theme.defaultPadding})`,
    background: theme.backgroundColor,
    margin: theme.defaultPadding,
    position: 'absolute',
    borderBottom: '1px solid #ccc'
  },
  marginContainer: {
    width: `calc(100% - 1 * ${theme.defaultPadding}) !important`,
    height: `calc(100% - 2 * ${theme.defaultPadding}) !important`,
    margin: theme.defaultPadding,
    marginRight: 0,
    backgroundColor: theme.backgroundColor
  }
})

function mapStateToPropsDesktop(state) {
  return {
    custom: state.custom,
    tables: state.tableLists,
    floorPlan: state.floorPlan,
    selectedTable: state.selectedTable,
    showTableInfo: state.showTableInfo
  }
}

function mapStateToPropsMobile(state) {
  return {
    custom: state.custom,
    tables: state.tableLists
  }
}


const MobileRenderer = connect(mapStateToPropsMobile, null)(injectSheet(styles)(MobileTableListScreenRenderer))
const DesktopRenderer = connect(mapStateToPropsDesktop, null)(injectSheet(styles)(DesktopTableListScreenRenderer))

export { MobileRenderer, DesktopRenderer }
