import React from 'react';

export default class ChatButton extends React.Component {
    constructor(props) {
        super(props);

        this.props = props;
    }

    render() {
        return (
            <div>
                <div className="chat-icon glyphicon glyphicon-large glyphicon-comment" onClick={this.props.onClick}/>
                <span className="badge badge-notify">{this.props.unreadMessages > 0 ? this.props.unreadMessages : ''}</span>
            </div>
        )
    }
}
