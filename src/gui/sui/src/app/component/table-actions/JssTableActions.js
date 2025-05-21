import injectSheet from 'react-jss'
import TableActions from './TableActions'

// eslint-disable-next-line no-unused-vars
const styles = (theme) => ({
  actionButton: {
    backgroundColor: 'rgb(221, 221, 221)',
    border: '1px solid',
    margin: '0.5vh 0.5vw',
    height: 'calc(100% - 1vh)',
    width: 'calc(100% - 1vw)',
    borderRadius: '2px',
    color: 'rgb(0, 0, 0)'
  }
})

export default injectSheet(styles)(TableActions)
