import injectSheet from 'react-jss'
import SeatItems from './SeatItems'

const styles = () => {
  const containerMarginVertical = '0'
  const containerMarginHorizontal = '0'

  return {
    header: {
      backgroundColor: 'white',
      display: 'flex',
      alignItems: 'center'
    },
    seatIcon: {
      margin: '0.5vh 1vw 0.5vh 1vw'
    },
    rootContainer: {
      margin: `${containerMarginVertical}vh ` +
              `${containerMarginHorizontal}vw ` +
              `${containerMarginVertical}vh ` +
              `${containerMarginHorizontal}vw`,
      width: `calc(100% - ${2 * containerMarginHorizontal}vw)`,
      height: `calc(100% - ${2 * containerMarginVertical}vh)`,
      display: 'flex',
      flexDirection: 'column',
      '& .scroll-panel-items': {
        padding: '0 0.5vw 0 0.5vw',
        width: 'calc(100% - 1vw)',
        fontWeight: 'normal'
      }
    },
    customSalePanelHeaderTitle: {
      margin: '0'
    },
    customSalePanelHeaderInfo: {
      display: 'flex',
      background: 'white'
    },
    customSalePanelHeaderColumnLeft: {
      flex: '1',
      textAlign: 'left',
      margin: '0',
      fontWeight: 'bold',
      fontSize: '2vh'
    },
    customSalePanelHeaderColumnRight: {
      margin: '0.6vh',
      fontSize: '1.4vmin',
      fontWeight: 'bold'
    },
    seatItem: {
      textOverflow: 'ellipsis',
      overflow: 'hidden',
      whiteSpace: 'pre',
      margin: '0',
      padding: '0.5vmin'
    }
  }
}

export default injectSheet(styles)(SeatItems)
