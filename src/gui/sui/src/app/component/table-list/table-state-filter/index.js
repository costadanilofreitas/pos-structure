import injectSheet, { jss } from 'react-jss'

import TableStateFilter from './TableStateFilter'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = (theme) => ({
  buttonStyleActive: {
    flex: '1',
    backgroundColor: theme.pressedBackgroundColor,
    color: theme.activeColor,
    height: 'auto'
  }
})

export default injectSheet(styles)(TableStateFilter)
