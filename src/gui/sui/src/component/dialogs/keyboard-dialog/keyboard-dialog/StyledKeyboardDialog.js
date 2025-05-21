import styled from 'styled-components'

export const MessageBackground = styled.div`
  position: absolute;
  background-color: ${props => props.theme.modalOverlayBackground};
  top: 0;
  left: 0;
  height: 100%;
  width: 100%;
  z-index: 4;
  align-items: center;
  justify-content: center;
`

export const MessageTitleContainer = styled.div`
  height: 100%;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
`

export const MessageTitle = styled.div`
  height: ${props => props.flat ? '100%' : 'calc(100% - 2vmin)'};
  width: ${props => props.flat ? '100%' : 'calc(100% - 2vmin)'};
  border-radius: ${props => props.flat ? ' none ' : ' 1vmin '};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3.0vmin;
  font-weight: bold;
  color: ${props => props.theme.pressedColor};
  background-color: ${props => props.flat ? props.theme.pressedBackgroundColor : props.theme.activeBackgroundColor}; 
`

export const ButtonsContainer = styled.div`
  height: ${props => props.flat ? '100%' : 'calc(100% - 2vmin)'};
  margin: ${props => props.flat ? 'none' : '1vmin'};
  border-radius: ${props => props.flat ? ' none ' : ' 1vmin '};
  font-size: 2vmin;
  flex: 1;
  display: flex;
`

export const Messages = styled.div`
  margin: ${props => !props.flat && !props.vertical && !props.hideKeys ? '1vmin 1vmin 0vmin 1vmin' : 'none'};
  border-radius: ${props => props.flat ? ' none ' : ' 1vmin '};
  position: relative;
  top: ${props => props.vertical || props.hideKeys ? '32.5%' : '16%'};
  width: ${props => props.vertical || props.hideKeys ? '100%' : '70%'};
  min-height: ${props => props.minHeight};
  left: ${props => props.vertical || props.hideKeys ? 'none' : '15%'};
  background: ${props => props.hideKeys ? props.theme.titleBackgroundColor : props.theme.popupsBackgroundColor};
  display: flex;
  overflow: hidden;
  flex-direction: column;
`

export const CenterInput = styled.div`
  border-radius: ${props => props.flat ? ' none ' : ' 1vmin '};
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
`

export const Comments = styled.div`
  border-radius: ${props => props.flat ? ' none ' : ' 1vmin '};
  width: 100%;
  height: 100%;
  border-right: 1px solid #CCC;
`

export const CommentLine = styled.p`
  border-radius: ${props => props.flat && props.selected ? ' none ' : ' 1vmin '};
  background: ${props => props.selected ? props.theme.activeBackgroundColor : 'none'};
  color: ${props => props.selected ? ' #FFFFFF ' : ' none '};
  margin: 0;
  height: 100%;
  padding: 1vh;
  font-size: 3vmin;
  text-align: justify;
  min-height: 3vmin;
`
export const Input = styled.div`
  display: flex;
  height: 100%;
  justify-content: center;
  align-items: center;
`

export const KeyboardInputRoot = styled.div`
  composes: keyboard-input-root;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
`

export const KeyboardInputCont = styled.div`
  border-radius: ${props => props.flat ? ' none ' : ' 1vmin '};
  composes: keyboard-input-cont;
  display: flex;
  background-color: ${props => props.theme.inputBackground};
  align-items: center;
  position: relative;
  width: ${props => props.flat ? ' 100% ' : ' 95% '};
  height: ${props => props.flat ? ' 100% ' : ' 70% '}; 
`

export const KeyboardInputWrapper = styled.div`
  composes: keyboard-input-wrapper;
  position: relative;
  padding-top: 0.7vmin;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  align-self: center;
  padding-bottom: 0.7vmin;
  padding-left: 1vmin;
  flex-grow: 1;
  flex-shrink: 1;
  flex-basis: 0;
  box-sizing: border-box;
`

export const KeyboardInput = styled.div`
  composes: keyboard-input;
  width: 100%;
  font-size: 3vmin;
  outline: none;
  border: none;
  font-weight: bold;
  text-align: left;
  font-family: sans-serif, monospace;
  &::selection {
    background-color: black;
    color: white;
  }
  &:placeholder-shown {
    font-size: 2.5vmin;
    font-weight: normal;
    font-family: Arial Bold, Arial;
  }
`

export const KeyboardInputBackspaceRoot = styled.div`
  composes: keyboard-input-backspace-root;
  position: relative;
  width: 100%;
  height: 100%;
  padding: ${props => props.paddingBackspace ? 'none' : '1vmin 2%'};
  flex: 0;
  box-sizing: border-box;
  display: flex;
  justify-content: center;
  align-items: center;
  color: ${props => props.theme.inputBackSpaceColor};
`

export const KeyboardHideShow = styled.div`
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  color: ${props => props.theme.inputBackSpaceColor};
`
