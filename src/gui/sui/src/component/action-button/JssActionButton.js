import injectSheet from 'react-jss'
import ActionButton from './ActionButton'

const button = {
  border: '0px solid',
  height: '100%',
  width: '100%',
  display: 'block',
  alignItems: 'center',
  justifyContent: 'center',
  padding: '5px'
}

const styles = (theme) => ({
  activeButton: Object.assign({
    backgroundColor: theme.activeBackgroundColor,
    color: theme.activeColor,
    '&:not(:last-child)': {
      borderRight: 'solid 1px #fff'
    }
  }, button),
  disabledButton: Object.assign({
    backgroundColor: theme.disabledBackgroundColor,
    color: theme.disabledColor
  }, button),
  pressedButton: Object.assign({
    backgroundColor: theme.pressedBackgroundColor,
    color: theme.pressedColor
  }, button),
  inlineText: {
    display: 'flex'
  }
})

export default injectSheet(styles)(ActionButton)
