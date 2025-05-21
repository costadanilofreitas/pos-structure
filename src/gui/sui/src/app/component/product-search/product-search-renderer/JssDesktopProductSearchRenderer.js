import injectSheet from 'react-jss'

import DesktopProductSearchRenderer from './DesktopProductSearchRenderer'

const styles = (theme) => ({
  container: {
    position: 'absolute',
    display: 'flex',
    flexDirection: 'column',
    width: '100%',
    height: '100%',
    borderTop: theme.defaultComponentBorder,
    boxSizing: 'border-box'
  }
})
export default injectSheet(styles)(DesktopProductSearchRenderer)
