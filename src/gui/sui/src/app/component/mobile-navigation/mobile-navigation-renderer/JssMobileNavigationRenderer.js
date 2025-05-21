import injectSheet from 'react-jss'

import MobileNavigationRenderer from './MobileNavigationRenderer'


const styles = (theme) => ({
  divButton: {
    height: 'calc(100% / 12)',
    width: `calc(100% - 2 * ${theme.defaultPadding})`,
    padding: `0 calc(${theme.defaultPadding}) 0 calc(${theme.defaultPadding})`
  },
  paddingButtonPrevious: {
    backgroundColor: 'rgb(255, 215, 0)',
    color: theme.fontColor
  },
  grid: {
    padding: '1vh'
  }
})

export default injectSheet(styles)(MobileNavigationRenderer)
