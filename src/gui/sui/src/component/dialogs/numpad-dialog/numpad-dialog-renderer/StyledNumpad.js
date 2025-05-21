import styled from 'styled-components'

import ActionButton from '../../../../component/action-button'
import ScreenOrientation from '../../../../constants/ScreenOrientation'

export const AbsoluteWrapper = styled.div`
  position: absolute;
  height: 100% ;
  width: 100%;
`
export const NumpadBackground = styled.div`
  position: absolute;
  height: 100% ;
  width: 100%;
  background-color: ${props => props.theme.modalOverlayBackground};
  top: 0;
  left: 0;
  z-index: 5;
  display: flex;
  align-items: center;
  justify-content: center;
`
export const Numpad = styled.div`
  margin: ${props => props.flat || props.mobile ? ' none ' : props.theme.defaultMargin};
  position: relative;
  height: ${props => props.screenOrientation === ScreenOrientation.Portrait ? ' calc(100% / 12 * 5) ' : 'calc(100% / 12 * 8)'};
  width: ${props => props.screenOrientation === ScreenOrientation.Portrait || props.mobile ? ' 100% ' : '40%'};
  border-radius: ${props => props.flat ? ' 0 ' : ' 1vmin '};
  background-color: ${props => props.theme.popupsBackgroundColor};
  flex-direction: column;
  display: flex;
  align-items: center;
  justify-content: center;
  @media (max-width: 720px) {
    width: 100%;
    height: calc(100% / 12 * 8);
  }
`
export const NumpadContainer = styled.div`
  height: ${props => props.flat ? '100%' : 'calc(100% - 2vmin)'};
  width: ${props => props.flat ? '100%' : 'calc(100% - 2vmin)'};
  position: relative;
  border-radius: ${props => props.flat ? ' 0 ' : ' 2vmin '};
  flex: ${props => props.screenOrientation === ScreenOrientation.Portrait ? ' 3 ' : ' 6 '};
  display: flex;
`

export const NumpadBoxTitleContainer = styled.div`
  height: 100%;
  width: 100%;
  display: flex;
  flex: 1;
  justify-content: center;
  align-items: center;
`

export const NumpadBoxTitle = styled.div`
  height: ${props => props.flat ? '100%' : 'calc(100% - 2vmin)'};
  width: ${props => props.flat ? '100%' : 'calc(100% - 2vmin)'};
  border-radius: ${props => props.flat ? 'none' : '1vmin'};
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: 2.5vmin;
  font-weight: bold;
  color: ${props => props.theme.activeColor};
  background-color: ${props => props.flat ? props.theme.dialogTitleBackgroundColor
    : props.theme.activeBackgroundColor}; 
`

export const NumpadTitle = styled.div`
  display: ${props => props.flat ? 'flex' : 'block'};
  flex-direction: column;
  align-items: center;
  justify-content: center;
`

export const NumpadTitleText = styled.div`
  float: left;
  margin-right: 1vmin;
  text-align: center;
`

export const NumpadKeys = styled(ActionButton)`
  background: ${props => props.theme.backgroundColor} !important;
  color: ${props => props.theme.fontColor} !important;
  font-weight: normal;
  composes: numpad-button;
  border: none;
  width: 100%;
  height: 100%;
  font-size: 4.5vmin !important;
  outline: none;
  border-radius: 0;
  &:active {
    background: ${props => props.theme.pressedBackgroundColor};
    color: ${props => props.theme.pressedColor};
  }
  &:focus {
    outline: 0
  }
`

export const NumpadButtons = styled.div`
  height: 100%;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  border-radius: ${props => props.flat ? ' 0 ' : ' 1vmin '};
  flex: 1;
  font-size: 2vmin;
`

