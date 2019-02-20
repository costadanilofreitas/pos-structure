import React from 'react';
import axios from 'axios'
import config from './config/index'
import Keyboard, {KeyboardButton, LatinLayout} from 'react-screen-keyboard';
import * as moment from 'moment'

export class Chat extends React.Component {
    constructor(props) {
        super(props);

        this.chatInput = null;

        this.state = {chatInput: null};

        this.retrievingMessages = false;

        this.sendMessage = this.sendMessage.bind(this);
        this.convertMessagesToChatText = this.convertMessagesToChatText.bind(this);
    }

    componentDidUpdate() {
        if(this.textArea !== null) {
            this.textArea.scrollTop = this.textArea.scrollHeight;
        }
    }

    convertMessagesToChatText(messages) {
        return (<div>
            {messages.map(message => <p key={message.id}><em>{moment(message.createdTime).format("DD/MM/YYYY HH:mm:ss")}</em>&nbsp;<strong>{message.from === "Store" ? "Loja" : "Sac"}</strong>:&nbsp;{message.text}</p>)}
        </div>);
    }

    sendMessage() {
        if(this.chatInput.value.trim() === "") {
            this.chatInput.value = "";
            return
        }

        let message = {};
        message.text = this.chatInput.value;

        this.sendingMessage = true;
        this.chatInput.disabled = true;
        let that = this;

        axios.post(config.apiBaseUrl + "/chat/sendMessage", message, {headers: {"Content-Type": "text/plain"}})
            .then(response => {
                that.chatInput.value = "";
                this.props.getUpdates();
            })
            .catch(error => {
                alert("Erro enviando mensagem")
            });
    }

    render() {
        let chatText = this.convertMessagesToChatText(this.props.messages);

        /*
        50: footer
        350: keyboard
        34: input
        30: margin top(10), margin messages/keyboard(10), margin-bottom(10)
         */
        let textAreaHeight = window.innerHeight - 50 - 350 - 34 - 30;

        let messagesHeightStyle = {height: textAreaHeight};

        let messagesScrollStyle = {height: textAreaHeight, overflowY: "scroll"};

        let that = this;

        return (
            <div className="chat-container">
                <div className="messages-container">
                    <div style={messagesHeightStyle} className="row">
                        <div style={messagesHeightStyle} className="col-xs-12 chat-messages-container">
                            <div style={messagesScrollStyle} className="form-control chat-messages" ref={textArea => this.textArea = textArea}>
                                {chatText}
                            </div>
                        </div>
                    </div>
                    <div className="row">
                        <div className="col-xs-12">
                            <input className="form-control" type="text" ref={input => {
                                if(that.chatInput === null && input !== null)
                                {
                                    that.chatInput = input;
                                    this.forceUpdate();
                                }
                            }}/>
                        </div>
                    </div>
                </div>
                {that.chatInput !== null &&
                <Keyboard
                    inputNode={that.chatInput}
                    rightButtons={[
                        <KeyboardButton
                            onClick = {this.sendMessage}
                            value="Enviar"
                            classes="keyboard-submit-button"
                        />
                    ]}
                    layouts={[LatinLayout]}
                />}
            </div>
            )
    }
}