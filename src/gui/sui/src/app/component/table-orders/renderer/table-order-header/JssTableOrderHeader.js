import injectSheet from 'react-jss'
import TableOrderHeader from './TableOrderHeader'

// eslint-disable-next-line no-unused-vars
const styles = (theme) => ({
  customSalePanelHeader: {
    backgroundColor: 'white',
    color: 'black',
    fontWeight: 'bold',
    fontSize: '1.5vmin',
    width: '100%',
    height: '100%'
  },
  customSalePanelHeaderTitle: {
    display: 'flex'
  },
  customSalePanelHeaderTitleColumnLeft: {
    margin: '0'
  },
  headerInnerInfo: {
    fontSize: '2.5em'
  },
  displayCenteredRightItem: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end'
  },
  displayCenteredLeftItem: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-start'
  },
  faHandIcon: {
    float: 'right',
    margin: '0.4vw'
  },
  customSalePanelHeaderTitleColumnRight: {
    margin: '0',
    alignItems: 'center',
    display: 'flex',
    justifyContent: 'flex-end',
    padding: '0 0.5vw 0 0',
    '& span': {
      margin: '0 0.2vh;'
    }
  },
  customSalePanelHeaderColumnLeft: {
    textAlign: 'left',
    margin: '0'
  },
  customSalePanelHeaderColumnRight: {
    textAlign: 'right',
    margin: '0 0.5vw 0 0'
  }
})

export default injectSheet(styles)(TableOrderHeader)
