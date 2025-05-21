import injectSheet from 'react-jss'
import LoginInfoRenderer from './LoginInfoRenderer'

const styles = (theme) => ({
  container: {
    padding: theme.defaultPadding,
    height: `calc(100% - 2 * ${theme.defaultPadding})`,
    width: `calc(100% - 2 * ${theme.defaultPadding})`,
    fontSize: '2.80vmin'
  }
})

export default injectSheet(styles)(LoginInfoRenderer)
