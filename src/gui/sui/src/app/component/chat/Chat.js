import React, { Component } from 'react'
import ChatRenderer from './chat-renderer/ChatRenderer'
import PropTypes from 'prop-types'


class Chat extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    return (
      <ChatRenderer {...this.props}/>
    )
  }
}

Chat.propTypes = {
  newMessagesCount: PropTypes.number,
  resetMessageCount: PropTypes.func
}

export default Chat
