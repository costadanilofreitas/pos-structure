import injectSheet from 'react-jss'
import TableWarns from './TableWarns'

const styles = (theme) => ({
  detailsTitle: {
    fontSize: '1.8vmin',
    fontWeight: 'bold',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    background: theme.dialogTitleBackgroundColor,
    color: '#FFFFFF'
  },
  warnsLine: {
    fontSize: '1.5vmin',
    width: '100%'
  },
  centerIcon: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center'
  },
  centerTable: {
    display: 'flex',
    justifyContent: 'flex-start',
    alignItems: 'center',
    margin: `0 0 0 ${theme.defaultPadding}`,
    width: `calc(100% - ${theme.defaultPadding})`
  }
})

export default injectSheet(styles)(TableWarns)
