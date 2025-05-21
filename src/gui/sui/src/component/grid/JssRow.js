import injectSheet from 'react-jss'
import Row from './Row'

const styles = (theme) => ({
  row: {
    marginBottom: theme.rowSpace || 0
  }
})

export default injectSheet(styles)(Row)
