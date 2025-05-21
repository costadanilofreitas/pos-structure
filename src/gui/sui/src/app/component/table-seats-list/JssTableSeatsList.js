import injectSheet from 'react-jss'
import TableSeatsList from './TableSeatsList'

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
  tableHeader: {
    position: 'relative',
    flex: '4',
    color: 'black',
    fontWeight: 'bold',
    textAlign: 'center',
    fontSize: '3vmin',
    padding: '2vmin',
    background: 'rgba(0, 178, 169, 0.26)'
  },
  singleSeatContainerDesktop: {
    margin: `calc( ${theme.defaultPadding} /2)`,
    width: `calc((100% / 3) - ${theme.defaultPadding})`,
    height: `calc((100% / 2) - ${theme.defaultPadding})`,
    float: 'left'
  },
  singleSeatContainerMobile: {
    margin: `calc( ${theme.defaultPadding} /2)`,
    width: `calc((100% / 1) - ${theme.defaultPadding})`,
    height: `calc((100% / 2) - ${theme.defaultPadding})`,
    float: 'left'
  }
})

export default injectSheet(styles)(TableSeatsList)
