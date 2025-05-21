import injectSheet from 'react-jss'
import LoginNumpadRenderer from './LoginNumpadRenderer'

const styles = (theme) => ({
  loginNumPadContainer: {
    backgroundColor: theme.loginScreenBackgroundColor,
    height: '100%'
  },
  blockMessageContainer: {
    height: '100%',
    width: '100%',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    textAlign: 'center',
    fontSize: '3em'
  }
})

export default injectSheet(styles)(LoginNumpadRenderer)
