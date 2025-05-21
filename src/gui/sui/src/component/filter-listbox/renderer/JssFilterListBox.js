import injectSheet from 'react-jss'

import FilterListBoxRenderer from './FilterListBoxRenderer'


const styles = (theme) => ({
  absoluteWrapper: {
    position: 'absolute',
    height: '100%',
    width: '100%',
    background: theme.backgroundColor
  },
  filterListBoxTitle: {
    fontSize: '2.5vmin',
    fontWeight: 'bold',
    height: '100%',
    display: 'flex',
    textAlign: 'center',
    alignItems: 'center',
    width: '100%',
    justifyContent: 'center',
    color: theme.pressedColor,
    backgroundColor: theme.pressedBackgroundColor
  },
  listItem: {
    fontSize: '2vmin',
    textAlign: 'center',
    margin: '0',
    padding: '1vh'
  },
  listItemNoFilter: {
    fontSize: '3vmin',
    textAlign: 'center',
    margin: '0',
    padding: '1vh'
  },
  listItemSelected: {
    color: theme.activeColor,
    backgroundColor: theme.activeBackgroundColor
  },
  numPadContainer: {
    height: '100%',
    width: '100%'
  }
})

export default injectSheet(styles)(FilterListBoxRenderer)
