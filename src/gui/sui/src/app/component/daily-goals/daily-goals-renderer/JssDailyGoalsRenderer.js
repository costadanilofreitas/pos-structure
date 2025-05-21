import injectSheet from 'react-jss'
import DailyGoalsRenderer from './DailyGoalsRenderer'
import withState from '../../../../util/withState'

const styles = (theme) => ({
  dailyGoalsMainContainer: {
    width: `calc(100% - 2 * ${theme.defaultPadding})`,
    height: `calc(100% - 2 * ${theme.defaultPadding})`,
    margin: theme.defaultPadding
  },
  tableContainer: {
    display: 'block',
    margin: '2em auto',
    width: '90%',
    maxWidth: '600px',
    border: '1px solid'
  },
  flexTable: {
    display: 'flex',
    flexFlow: 'row wrap',
    fontSize: '2.5vmin'
  },
  flexTableTitle: {
    display: 'flex',
    flexFlow: 'row wrap',
    background: theme.titleBackgroundColor,
    fontSize: '2.5vmin'
  },
  flexTableSelected: {
    display: 'flex',
    flexFlow: 'row wrap',
    background: theme.dailyGoalsColorReached,
    fontSize: '2.5vmin'
  },
  flexRow: {
    width: 'calc(100% / 4)',
    textAlign: 'center',
    fontWeight: 'normal'
  },
  centerItems: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    '& text': {
      fontSize: '1.5vmin'
    }
  },
  chartTitle: {
    textAlign: 'center',
    fontSize: '1.8vmin',
    fontWeight: 'bold',
    margin: theme.defaultPadding
  },
  chartInfo: {
    textAlign: 'center',
    margin: theme.defaultPadding,
    display: 'flex',
    alignItems: 'center',
    fontSize: '1.8vmin',
    fontWeight: 'bold'
  },
  chartInfoSquareGoal: {
    textAlign: 'center',
    height: '2vmin',
    width: '2vmin',
    margin: '0 1vh',
    background: theme.dailyGoalsColorReached
  },
  chartInfoSquareReached: {
    textAlign: 'center',
    height: '2vmin',
    width: '2vmin',
    margin: '0 1vh',
    background: theme.dailyGoalsColor
  },
  oneChart: {
    height: '50%'
  },
  dailyGoalsColorReached: {
    fill: theme.dailyGoalsColorReached,
    stroke: theme.dailyGoalsColorReached
  },
  dailyGoalsColor2: {
    fill: theme.dailyGoalsColor,
    stroke: theme.dailyGoalsColor
  }
})

export default injectSheet(styles)(withState(DailyGoalsRenderer, 'theme'))
