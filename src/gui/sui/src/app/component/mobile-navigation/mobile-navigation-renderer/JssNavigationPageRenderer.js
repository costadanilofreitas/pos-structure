import injectSheet from 'react-jss'

import NavigationPageRenderer from './NavigationPageRenderer'


const styles = (theme) => ({
  gridCategory: {
    overflowY: 'scroll',
    height: `calc(100% - 2 * ${theme.defaultPadding})`,
    width: `calc(100% - 2 * ${theme.defaultPadding})`,
    padding: `calc(${theme.defaultPadding})`
  },
  divButton: {
    height: 'calc(100% / 12)',
    width: `calc(100% - 2 * ${theme.defaultPadding})`,
    padding: `0 calc(${theme.defaultPadding}) 0 calc(${theme.defaultPadding})`
  },
  paddingButtonCategory: {
    height: 'calc(100vh / 12)',
    display: 'flex'
  },
  grid: {
    padding: '1vh'
  },
  backButton: {
    color: 'red',
    backgroundColor: 'blue'
  },
  backButtonRow: {
    height: 'calc(100vh / 12)'
  },
  categoryWithBorder: {
    height: '100%',
    '&::after': {
      content: '""',
      position: 'absolute',
      top: '-3px',
      right: '-3px',
      width: '0',
      height: '0',
      borderStyle: 'solid',
      borderWidth: '15px',
      borderColor: `transparent ${theme.backgroundColor} ${theme.backgroundColor} transparent`,
      transform: 'rotate(270deg)'
    }
  },
  category: {
    height: '100%'
  },
  noNavigation: {
    height: '100%',
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  }
})

export default injectSheet(styles)(NavigationPageRenderer)
