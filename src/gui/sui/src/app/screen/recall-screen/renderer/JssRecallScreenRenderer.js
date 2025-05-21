import injectSheet from 'react-jss'
import RecallScreenRenderer from './RecallScreenRenderer'


const styles = (theme) => ({
  titleContainer: {
    margin: `${theme.defaultPadding} ${theme.defaultPadding} 0 ${theme.defaultPadding}`,
    backgroundColor: theme.backgroundColor
  },
  detailsTitle: {
    fontSize: '2.5vmin',
    fontWeight: 'bold',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    textTransform: 'uppercase',
    backgroundColor: theme.backgroundColor,
    borderBottom: '5px solid #DCDDDE !important'
  },
  refresh: {
    height: `calc(100% - ${theme.defaultPadding})`,
    color: `${theme.fontColor}!important`
  },
  ordersCont: {
    margin: `0 ${theme.defaultPadding} ${theme.defaultPadding} ${theme.defaultPadding}`
  },
  ordersPanel: {
    backgroundColor: theme.backgroundColor
  },
  buttonsContainer: {
    height: '6vmin !important',
    width: 'calc(100% / 12 * 1)',
    '& button': {
      borderRight: 'solid 1px #fff'
    }
  },
  scheduledTime: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'column',
    border: '1px solid #ccc',
    height: 'calc(100% - 2px) !important',
    width: 'calc(100% - 2px) !important'
  },
  orders: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    boxSizing: 'border-box',
    textAlign: 'center',
    '& .receiveTime': {
      wordSpacing: '9999px'
    }
  },
  loadingSpinner: {
    composes: 'fa fa-spinner fa-spin fa-4x loading-screen-spinner',
    color: '#777777',
    width: '64px',
    height: '64px',
    position: 'fixed',
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
    margin: 'auto',
    maxWidth: '100%',
    maxHeight: '100%',
    overflow: 'hidden'
  },
  centeredDiv: {
    display: 'flex',
    height: '100%',
    width: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'absolute'
  },
  numberCircle: {
    borderRadius: '50%',
    width: '1.8vmin',
    height: '1.8vmin',
    padding: '0.5em',
    background: theme.iconColor,
    color: theme.activeColor,
    marginLeft: '1vmin',
    marginRight: '1vmin',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center'
  },
  partnerVoided: {
    backgroundColor: '#ec8585 !important'
  }
})

export default injectSheet(styles)(RecallScreenRenderer)
