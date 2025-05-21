import injectSheet from 'react-jss'
import TableStateList from './TableStateList'
import withStaticConfig from '../../../util/withStaticConfig'


const styles = (theme) => ({
  containerStyle: {
    height: `calc(100% - ${theme.defaultPadding})`,
    width: '100%',
    margin: `${theme.defaultPadding} 0 0 0`
  },
  containerListStyle: {
    display: 'flex',
    position: 'relative',
    flex: '100',
    flexDirection: 'row',
    flexWrap: 'wrap',
    alignContent: 'flex-start',
    height: '100%'
  }
})

export default injectSheet(styles)(withStaticConfig(TableStateList))
