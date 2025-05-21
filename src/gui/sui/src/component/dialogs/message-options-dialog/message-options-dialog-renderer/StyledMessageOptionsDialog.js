import styled from 'styled-components'

export const MessageBackground = styled.div`
    position: absolute;
    background-color: ${props => props.theme.modalOverlayBackground};
    top: 0;
    left: 0;
    height: 100%;
    width: 100%;
    z-index: 5;
    display: flex;
    align-items: center;
    justify-content: center;
`
export const Message = styled.div`
    border-radius: ${props => props.flat ? ' none ' : ' 1vmin '};
    position: relative;
    width: ${props => props.messageWidth};
    height: ${props => props.messageHeight};
    background-color: ${props => props.theme.popupsBackgroundColor};
    display: flex;
    flex-direction: column;
    @media (max-width: 720px) {
      width: 100%;
      height: calc(100% / 12 * 7);
    }
`
export const MessageContainer = styled.div`
    background-color: ${props => props.theme.popupsBackgroundColor};
    text-align: center;
    font-size: 2.5vmin;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
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
    border-radius: ${props => props.flat ? ' none ' : '1vmin'};
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3.0vmin;
    font-weight: bold;
    color: ${props => props.theme.pressedColor};
    background-color: ${props => props.theme.pressedBackgroundColor};
 `

export const ButtonsContainer = styled.div`
    height: ${props => props.flat ? '100%' : 'calc(100% - 2vmin)'};
    width: ${props => props.flat ? '100%' : 'none)'};
    margin: ${props => props.flat ? ' none ' : '0 0.5vmin 0 0.5vmin'};
    border-radius: ${props => props.flat ? 'none' : '1vmin'};
    font-size: 2vmin;
    height: 100%;
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: ${props => props.theme.popupsBackgroundColor};
`

export const MessageButton = styled.div`
    height: 100%;
    width: ${props => props.flat ? '100%' : 'calc(100% - 1vmin)'};
    margin: ${props => props.flat ? ' none ' : '0 0.5vmin 0 0.5vmin'};
    border-radius: ${props => props.flat ? ' 0 ' : ' 1vmin '};
    flex: 1;
    color: ${props => props.theme.pressedColor};
    background-color: ${props => props.theme.dialogButtonBackgroundColor}; 
    border: none;
    position: relative;
    bottom: ${props => props.flat ? 'none' : '1vmin'};
    display: flex;
    text-transform: capitalize;
    align-items: center;
    justify-content: center;
    &:not(:last-child) {
      border-right: solid 1px #fff;
    }
    &:focus {
      outline: 0
    }
`

export const MainMessageContainer = styled.div`
    display: flex;
    background-color: ${props => props.theme.popupsBackgroundColor};
    align-items: center;
    
    justify-content: center;
    height: 100%;
    width: 100%;
`
