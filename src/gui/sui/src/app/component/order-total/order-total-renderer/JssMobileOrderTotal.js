import injectSheet from 'react-jss'
import MobileOrderTotalRenderer from './MobileOrderTotalRenderer'

const styles = (theme) => ({
  container: {
    width: '100%',
    height: '100%',
    backgroundColor: theme.backgroundColor,
    color: theme.fontColor,
    fontSize: '3.0vmin'
  },
  textBounce: {
    animationName: 'textBounceAnimation',
    animationDuration: '0.3s',
    animationFillMode: 'none',
    animationDelay: 0,
    animationIterationCount: 1,
    animationTimingFunction: 'ease-out',
    animationDirection: 'normal'
  },
  '@keyframes textBounceAnimation': {
    '0%': {
      fontSize: '3.0vmin'
    },
    '10%': {
      fontSize: '3.6vmin'
    },
    '50%': {
      fontSize: '2.8vmin'
    },
    '70%': {
      fontSize: '3.1vmin'
    },
    '100%': {
      fontSize: '3.0vmin'
    }
  },
  saleLine: {
    backgroundColor: theme.titleBackgroundColor,
    textAlign: 'center'
  },
  orderId: {
    backgroundColor: theme.titleBackgroundColor,
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    fontWeight: 'bold'
  },
  totalGross: {
    backgroundColor: theme.titleBackgroundColor,
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    fontWeight: 'bold'
  },
  emptyCart: {
    backgroundColor: theme.titleBackgroundColor,
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    fontWeight: 'bold',
    height: '100%'
  },
  underlineSaleLine: {
    width: '100%',
    height: '100%',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    fontWeight: 'bold'
  },
  popupHeight: {
    width: '100%',
    height: 'calc(100vh / 12 * 8)'
  },
  innerPopupContainer: {
    width: '100%',
    height: 'calc(100vh / 12 * 8)',
    zIndex: '4'
  },
  popContainer: {
    width: '100%',
    height: '100%'
  },
  iconAngle: {
    width: '100%',
    height: '100%',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.titleBackgroundColor
  },
  quantityContainer: {
    margin: `0 0 0 ${theme.defaultPadding}`,
    backgroundColor: theme.backgroundColor
  }
})

export default injectSheet(styles)(MobileOrderTotalRenderer)
