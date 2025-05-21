import PropTypes from 'prop-types'
import React from 'react'
import KeyboardInput from '../../../../component/dialogs/keyboard-dialog/keyboard-dialog/KeyboardInput'
import KeyboardWrapper from '../../../../component/dialogs/keyboard-dialog/keyboard-dialog/KeyboardWrapper'
import RendererChooser from '../../../../component/renderer-chooser'

export default class OrderSearchRenderer extends React.Component {
  constructor(props) {
    super(props)
    this.state = { showKeyboard: false }

    this.handleOnInputChange = this.handleOnInputChange.bind(this)
    this.handleShowHideKeyboardButton = this.handleShowHideKeyboardButton.bind(this)
  }

  handleShowHideKeyboardButton() {
    this.setState({ showKeyboard: !this.state.showKeyboard })
    this.props.onChange({ size: this.state.showKeyboard ? 1 : 6 })
  }

  handleOnInputChange(text) {
    this.props.onChange({ text })
  }

  render() {
    return (
      <RendererChooser
        desktop={
          <KeyboardWrapper
            handleOnInputChange={this.handleOnInputChange}
            value={this.props.value.text}
            keyboardVisible={this.state.showKeyboard}
            showHideKeyboardButton
            handleShowHideKeyboardButton={this.handleShowHideKeyboardButton}
            keyboardFlexSize={5}
            flat={true}
          />
        }
        mobile={
          <KeyboardInput flat
            flatStyle
            onInputChange={this.handleOnInputChange}
            value={this.props.value.text}
          />
        }
      />
    )
  }
}

OrderSearchRenderer.propTypes = {
  onChange: PropTypes.func,
  value: PropTypes.shape({
    text: PropTypes.string,
    size: PropTypes.number
  })
}
