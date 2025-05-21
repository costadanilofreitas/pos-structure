import injectSheet from 'react-jss'
import DektopRenderer from './DesktopTableOrdersRenderer'
import MobileRenderer from './MobileTableOrdersRenderer'

const styles = (theme) => ({
  absoluteWrapper: {
    position: 'absolute',
    height: '100%',
    width: '100%'
  },
  ordersContainer: {
    margin: `calc(${theme.defaultPadding}/ 2)`,
    height: `calc(100% - ${theme.defaultPadding}) !important`,
    width: `calc(100% - ${theme.defaultPadding}) !important`
  },
  buttonsContainer: {
    margin: `calc(${theme.defaultPadding} / 2)`
  },
  buttonContainer: {
    width: '50%',
    float: 'left',
    height: '100%'
  },
  button: {
    backgroundColor: 'white',
    color: 'white !important'
  },
  buttonPressed: {
    backgroundColor: 'black !important',
    color: 'white !important'
  },
  buttonDisabled: {
    backgroundColor: 'rgb(155, 155, 155) !important',
    color: 'white !important'
  },
  previousButton: {
    justifyContent: 'flex-start',
    paddingLeft: '1.5vw'
  },
  nextButton: {
    justifyContent: 'flex-end',
    paddingRight: '1.5vw'
  },
  rootContainer: {
    width: '100%',
    height: '100%',
    overflowY: 'scroll'
  },
  orderContainer: {
    width: '100%',
    height: 'calc(100% / 8)'
  }
})

const mobile = injectSheet(styles)(MobileRenderer)
const desktop = injectSheet(styles)(DektopRenderer)

export { desktop as DesktopTableOrdersRenderer, mobile as MobileTableOrdersRenderer }
