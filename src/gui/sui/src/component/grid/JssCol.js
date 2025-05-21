import injectSheet from 'react-jss'
import Col from './Col'

const styles = (theme) => ({
  col: {
    display: 'inline-block',
    height: '100%'
  },
  colInner: {
    height: '100%',
    paddingLeft: `calc(${theme.colSpace || 0}/ 2)`,
    position: 'relative'
  },
  lastColInner: {
    paddingRight: '0 !important'
  },
  firstColInner: {
    paddingLeft: '0 !important'
  },
  xs1: {
    width: 'calc(100% / 12)'
  },
  xs2: {
    width: 'calc(100% / 6)'
  },
  xs3: {
    width: 'calc(100% / 4)'
  },
  xs4: {
    width: 'calc(100% / 3)'
  },
  xs5: {
    width: 'calc(100% / 12 * 5)'
  },
  xs6: {
    width: 'calc(100% / 2)'
  },
  xs7: {
    width: 'calc(100% / 12 * 7)'
  },
  xs8: {
    width: 'calc(100% / 12 * 8)'
  },
  xs9: {
    width: 'calc(100% / 12 * 9)'
  },
  xs10: {
    width: 'calc(100% / 12 * 10)'
  },
  xs11: {
    width: 'calc(100% / 12 * 11)'
  },
  xs12: {
    width: 'calc(100%)'
  }
})

export default injectSheet(styles)(Col)
