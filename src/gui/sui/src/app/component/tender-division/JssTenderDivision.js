import injectSheet from 'react-jss'
import TenderDivision from './TenderDivision'

const styles = (theme) => ({
  titleContainer: {
    height: '100%',
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '2.5vmin',
    backgroundColor: theme.activeBackgroundColor,
    color: theme.activeColor
  },
  bigTenderDivText: {
    fontSize: '2vmin',
    whiteSpace: 'pre'
  }
})

export default injectSheet(styles)(TenderDivision)
