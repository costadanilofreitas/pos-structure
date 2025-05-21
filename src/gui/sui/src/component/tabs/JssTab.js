import injectSheet from 'react-jss'
import Tab from './Tab'

const styles = (theme) => ({
  tab: {
    display: 'inline-block',
    textAlign: 'center',
    cursor: 'pointer',
    backgroundColor: theme.screenBackground,
    height: `calc(100% - 5px - ${theme.defaultPadding})`,
    width: 'calc(100%)'
  },
  activeTab: {
    paddingTop: theme.defaultPadding,
    textTransform: 'uppercase',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    borderBottom: `5px solid ${theme.pressedBackgroundColor}`
  }
})

export default injectSheet(styles)(Tab)
