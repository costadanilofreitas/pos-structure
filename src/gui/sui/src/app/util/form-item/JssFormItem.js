import injectSheet from 'react-jss'
import FormItem from './FormItem'

const styles = (theme) => ({
  belowLabel: {
    fontSize: '0.80em'
  },
  belowInput: {
    display: 'block'
  },
  endLabel: {
    display: 'block',
    margin: theme.defaultPadding
  },
  endInput: {
    display: 'table-cell',
    width: '100%'
  },
  input: {
    borderBottom: '1px solid black'
  },
  label: {
  },
  textAlignCenter: {
    textAlign: 'center'
  },
  textAlignRight: {
    textAlign: 'right'
  }
})

export default injectSheet(styles)(FormItem)
