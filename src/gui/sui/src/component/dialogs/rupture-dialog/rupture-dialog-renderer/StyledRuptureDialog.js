import styled from 'styled-components'
import ActionButton from '../../../../component/action-button'

export const RuptureBackground = styled.div`
    position: absolute;
    background-color: ${props => props.theme.modalOverlayBackground};
    height: 100%;
    width: 100%;
    z-index: 5;
    display: flex;
    align-items: center;
    justify-content: center;
`
export const RuptureMainContainer = styled.div`
    position: relative;
    width: 100%;
    height: 100%;
    background: ${props => props.theme.popupsBackgroundColor};
    display: flex;
    flex-direction: column;
`
export const RuptureContainer = styled.div`
    background-color: ${props => props.theme.popupsBackgroundColor};
    text-align: center;
    font-size: 3.5vmin;
    font-weight: bold;
    height: 100%;
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
`
export const RuptureContainerLine = styled.div`
    background-color: ${props => props.theme.popupsBackgroundColor};
    text-align: center;
    font-size: 3.5vmin;
    font-weight: bold;
    height: 100%;
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    border-left: ${props => `${props.theme.defaultPadding} solid ${props.theme.screenBackground}`};
`
export const RuptureKeyboard = styled.div`
    background-color: ${props => props.theme.popupsBackgroundColor};
    text-align: center;
    height: 100%;
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
`
export const RuptureLabelsContainer = styled.div`
    background-color: ${props => props.theme.popupsBackgroundColor};
    text-align: center;
    font-size: 2.5vmin;
    height: 100%;
    width: 100%;
    display: flex;
    justify-content: space-around;
    align-items: center;
    border-top: ${props => `${props.theme.defaultPadding} solid ${props.theme.screenBackground}`};
`
export const RuptureLabel = styled.div`
    height: 100%;
    width: 100%;
    align-items: center;
    display: flex;
    justify-content: center;
`
export const RuptureLabelLine = styled.div`
    height: 100%;
    width: 100%;
    align-items: center;
    display: flex;
    justify-content: center;
    border-right: ${props => `${props.theme.defaultPadding} solid ${props.theme.screenBackground}`};
`
export const RuptureTitle = styled.div`
    height: 100%;
    flex: 1;
    font-size: 3.0vmin;
    font-weight: bold;
    justify-content: center;
    display: flex;
    align-items: center;
    text-align: center;
    color: ${props => props.theme.pressedColor};
    background-color: ${props => props.theme.pressedBackgroundColor};
 `
export const ButtonGridContainer = styled.div`
    flex: 1;
    display: flex;
`
export const RuptureButtonsContainer = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  align-items: center;
  font-size: 2vmin;
  height: 100%;
  border-left: ${props => `${props.theme.defaultPadding} solid ${props.theme.screenBackground}`};
  border-right: ${props => `${props.theme.defaultPadding} solid ${props.theme.screenBackground}`};
`
export const RuptureButton = styled(ActionButton)`
  height: 13vmin;
  width: 15vmin;
`
export const BottomButtonsContainer = styled.div`
    position: relative;
    background-color: ${props => props.theme.popupsBackgroundColor};
    flex: 1;
    height: 100%;
    width: 100%;
    display: flex;
    font-size: 2vmin;
`
export const IngredientContainer = styled.div`
    display: flex;
    justify-content: center;
    position: relative;
    font-size: 1.8vmin;
    
    &.selected {
      background-color: ${props => props.theme.pressedBackgroundColor};
      color: ${props => props.theme.pressedColor};
    };
`
export const BlankLabelContainer = styled.div`
    height: 100%;
    border-right: ${props => `${props.theme.defaultPadding} solid ${props.theme.screenBackground}`};
    border-left: ${props => `${props.theme.defaultPadding} solid ${props.theme.screenBackground}`};
`
export const Ingredient = styled.div`
    
`
export const Spinner = styled.div`
    color: #777777;
    width: 64px;
    height: 64px;
    position: absolute;
    top: calc(50% - 64px);
`
