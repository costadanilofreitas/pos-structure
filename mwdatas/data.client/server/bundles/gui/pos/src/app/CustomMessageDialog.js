import React, { PureComponent } from 'react'
import { MessageDialog } from 'posui/dialogs'

export default class CustomMessageDialog extends PureComponent {
  state = {
    height: null
  }
  componentDidMount() {
    this.computeHeight()
  }
  componentDidUpdate(prevProps) {
    const currentId = ((this.props.children || {}).props || {}).id
    const nextId = ((prevProps.children || {}).props || {}).id
    if (currentId !== nextId) {
      this.computeHeight()
    }
  }

  computeHeight() {
    const textElementHeight = document.querySelector('.message-dialog-root td span').getBoundingClientRect().height
    const windowElementHeight = window.innerHeight
    const size = (100 * (textElementHeight / windowElementHeight)) + 30
    this.setState({ height: `${size}%` })
  }
  render() {
    return <MessageDialog {...this.props} height={this.state.height}/>
  }
}
