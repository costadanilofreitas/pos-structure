import injectSheet from 'react-jss'
import ScrollTable from './ScrollTable'


const styles = {
  table: {
    fontSize: '1.5vh',
    borderTop: '1px solid #d7d7d7'
  },
  scrollTable: {
    width: '100%',
    height: '100%',
    display: 'flex'
  },
  tableContainer: {
    width: '100%',
    height: '100%'
  },
  scrollButtonsContainer: {
    display: 'flex'
  },
  scrollButton: {
    flex: '1',
    height: '100%',
    width: '100%',
    backgroundColor: 'white',
    color: '#777 !important',
    fontSize: '2vh',
    margin: '-1px 0',
    border: 'none',
    borderTop: '1px solid #d7d7d7',
    '&:active': {
      backgroundColor: '#777',
      color: '#eee !important'
    }
  },
  scrollButtonDisabled: {
    color: '#eee !important'
  }
}


export default injectSheet(styles)(ScrollTable)
