import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Launcher } from 'react-chat-window'

import { FlexChild, FlexGrid } from '3s-widgets'
import { ConfirmButton, KeyboardChild, MainContainer } from './StyledChat'
import KeyboardWrapper from '../../../../component/dialogs/keyboard-dialog/keyboard-dialog/KeyboardWrapper'
import StaticConfigPropTypes from '../../../../prop-types/StaticConfigPropTypes'
import { getJoinedAvailableSaleTypes, getShortedSaleTypes } from '../../../util/saleTypeConverter'


class ChatRenderer extends Component {
  constructor(props) {
    super(props)

    this.state = {
      time: Date.now(),
      messageIdList: [],
      messageList: [],
      isOpen: false,
      typedText: ''
    }

    this.updateDisplayedMessages()
  }

  render() {
    return (
      <MainContainer visible={this.state.isOpen}>
        <FlexGrid direction={'column'}>
          <FlexChild size={4}>
            <Launcher
              agentProfile={{ teamName: 'SAC' }}
              onMessageWasSent={this.handleNewUserMessage}
              handleClick={this.toggleChatPopUp}
              isOpen={this.state.isOpen}
              messageList={this.state.messageList}
              showEmoji={false}
              mute={true}
              newMessagesCount={this.props.newMessagesCount}
            />
          </FlexChild>
          <KeyboardChild size={5}>
            <KeyboardWrapper
              value={this.state.typedText}
              handleOnInputChange={this.handleOnKeyboardInputChange}
              handleOnOk={this.handleOnKeyboardOk}
              visible={this.state.isOpen}
              keyboardVisible={this.state.isOpen}
              showHideKeyboardButton={false}
              flat={false}
              rightButtons={this.renderConfirmButton()}
            />
          </KeyboardChild>
        </FlexGrid>
      </MainContainer>
    )
  }

  renderConfirmButton() {
    return [
      <ConfirmButton onClick={this.handleOnKeyboardOk} className={'fa fa-paper-plane fa-2x'} key={1} />
    ]
  }

  componentDidMount() {
    this.interval = setInterval(() => this.updateDisplayedMessages(), 5000)
  }

  handleOnKeyboardOk = () => {
    this.handleNewUserMessage(this.state.typedText)
  }

  handleOnKeyboardInputChange = (typedText) => {
    this.setState({ typedText })
  }

  handleNewUserMessage = (newMessage) => {
    const messageText = typeof newMessage === 'object' ? newMessage.data.text : newMessage
    if (messageText.length === 0) {
      return
    }
    this.props.msgBus.parallelSyncAction('send_chat_messages', messageText).then(response => {
      if (response.ok && response.data !== '') {
        this.updateDisplayedMessages()
        this.setState({ typedText: '' })
      } else {
        console.error('Error sending chat message')
      }
    })
  }

  toggleChatPopUp = () => {
    this.setState({ isOpen: !this.state.isOpen })
    this.props.resetMessageCount()
  }

  updateDisplayedMessages() {
    const joinedSaleTypes = getJoinedAvailableSaleTypes(this.props.staticConfig.availableSaleTypes)
    const saleTypes = getShortedSaleTypes(joinedSaleTypes)
    if (!saleTypes.includes('DL')) {
      return
    }
    this.props.msgBus.parallelSyncAction('update_chat_messages').then(response => {
      if (response.ok && response.data) {
        for (let i = 0; i < response.data.length; i++) {
          const messageData = response.data[i]
          const messageId = messageData.id
          const idList = this.state.messageIdList

          if (!this.state.messageIdList.includes(messageId)) {
            this.addMessage(messageData)
            idList.push(messageId)
            this.setState({ messageIdList: idList })
          }
        }
      } else {
        console.error('Error retrieving chat messages')
      }
    })
  }

  addMessage = (messageData) => {
    let author
    if (messageData.from === 'Store') {
      author = 'me'
    } else {
      author = 'them'
    }

    const messageText = messageData.text

    this.setState({
      messageList: [...this.state.messageList, {
        author: author,
        type: 'text',
        data: { text: messageText }
      }]
    })
  }
}

ChatRenderer.propTypes = {
  msgBus: PropTypes.shape({
    syncAction: PropTypes.func.isRequired,
    parallelSyncAction: PropTypes.func.isRequired
  }),
  newMessagesCount: PropTypes.number,
  resetMessageCount: PropTypes.func,
  staticConfig: StaticConfigPropTypes
}

export default ChatRenderer
