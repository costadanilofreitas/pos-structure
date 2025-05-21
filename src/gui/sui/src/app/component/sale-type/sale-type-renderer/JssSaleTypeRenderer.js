import injectSheet from 'react-jss'

import SaleTypeRenderer from './SaleTypeRenderer'

const styles = (theme) => ({
  container: {
    width: '100%',
    height: `calc(100% - ${theme.defaultPadding})`,
    padding: `${theme.defaultPadding} 0 0 0`
  },
  selected: {
    borderBottom: `0.7vmin solid ${theme.iconColor}`
  }
})

export default injectSheet(styles)(SaleTypeRenderer)
