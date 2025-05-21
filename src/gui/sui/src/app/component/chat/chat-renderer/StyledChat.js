import styled from 'styled-components'
import { FlexChild } from '3s-widgets'

const MainContainer = styled.div`
  display: flex;
  width: 100%;
  height: ${props => props.visible ? 'calc(100% - 1vh)' : '0%'};
  position: absolute;
  margin-top: 1vh;
  
  .sc-message--content.sent .sc-message--text {
    background-color: ${props => props.theme.activeBackgroundColor};
  }

  .sc-user-input, .sc-message--avatar, .sc-user-input--file-icon-wrapper {
    display: none;
  }
  
  .sc-user-input--text {
    width: 90%;
  }
  
  .sc-header {
    background-color: ${props => props.theme.pressedBackgroundColor};
    border-radius: 0;
    height: 100%;
    min-height: 0;
    flex: 1;
  }
  
  .sc-message-list {
    padding: 0;
    height: calc(100% - 1vh);
    margin-top: 1vh;
    min-height: 0;
    flex: 7;
  }
  
  .sc-open-icon, .sc-closed-icon {
    position: absolute;
    bottom: 0;
    right: 0;
  }
  
  .sc-launcher {
    position: relative;
    display: ${props => props.visible ? 'none' : 'block'};
    width: 5vmin;
    height: 5vmin;
    background-color: ${props => props.theme.iconColor};
    float: right;
    bottom: 0;
    right: 0;
    z-index: 2;
    font-size: 3vmin;
    line-height: 5vmin;
    color: ${props => props.theme.backgroundColor};;
    text-align: center;
  }
  
  .sc-launcher:before {
    content: "\\f4ad";
    font-family: "Font Awesome 5 Free";
    width: 5vmin;
    height: 5vmin;
  }
  
  .sc-open-icon, .sc-closed-icon {
    display: none;
  }
  
  .sc-chat-window { 
      position: absolute;
      width: 100%;
      height: 100%;
      max-height: none;
      right: 0;
      bottom: 0;
      border-radius: 0;
  }

  .sc-message { 
      width: 90%;
      text-transform: uppercase;
  }

  .sc-header--close-button, .sc-header--close-button:hover { 
      background-color: ${props => props.theme.pressedBackgroundColor};
      box-sizing: border-box;
  }
  
  .sc-new-messages-count {
    background: ${props => props.theme.iconColor};
    color: ${props => props.theme.activeColor};
    top: -1vmin;
    left: -2.5vmin;
    font-size: 1vmin;
  }
`

const KeyboardChild = styled(FlexChild)`
  width: 100%;
  height: 100%;
  background: ${props => props.theme.backgroundColor};
`

const ConfirmButton = styled.button`
  width: 25%;
  color: ${props => props.theme.pressedBackgroundColor};
  border: none;
  height: 7vmin;
  margin: 0.5vmin;
  display: flex;
  align-items: center;
  justify-content: space-around;
  font-size: 5vmin;
`

export {
  MainContainer, KeyboardChild, ConfirmButton
}
