import injectSheet from 'react-jss'

import MobileOrderFunctionsRendererRenderer from './renderer/MobileOrderFunctionsRenderer'
import DesktopOrderFunctionsRenderer from './renderer/DesktopOrderFunctionsRenderer'
import TotemOrderFunctionsRenderer from './renderer/TotemOrderFunctionsRenderer'

const styles = (theme) => ({
  functionButton: {
    backgroundColor: theme.tenderButtonsBackground,
    border: '0px solid',
    height: '100%',
    width: '100%',
    alignItems: 'center',
    color: theme.tenderButtonsColor,
    justifyContent: 'center',
    padding: '5px'
  },
  pressedFunctionButton: {
    backgroundColor: theme.tenderButtonsBackground,
    border: '0px solid',
    height: '100%',
    width: '100%',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '5px',
    color: theme.tenderButtonsColor
  },
  functionButtonMain: {
    flexGrow: '1',
    flexShrink: '0',
    flexBasis: 'calc(66% - 8px)'
  },
  contextButtonStyle: {
    height: '100%',
    width: '100%'
  },
  contextMenu: {
    border: '0',
    zIndex: '3',
    width: '100%'
  },
  popContainer: {
    width: '100%',
    height: '100%'
  },
  innerPopupContainer: {
    width: '100%',
    height: '100%'
  },
  outerPopUpContainer: {
    width: '100%',
    left: '0'
  }
})

const MobileRenderer = injectSheet(styles)(MobileOrderFunctionsRendererRenderer)
const DesktopRenderer = injectSheet(styles)(DesktopOrderFunctionsRenderer)
const TotemRenderer = injectSheet(styles)(TotemOrderFunctionsRenderer)

export { MobileRenderer, DesktopRenderer, TotemRenderer }
