import styled from 'styled-components'
import Button from '../../../../component/action-button/Button'


export const ButtonContent = styled(Button)`
  width: ${props => `calc(100% - ${props.buttonSpacing} - ${props.buttonSpacing})`};
  height: ${props => `calc(100% - ${props.buttonSpacing} - ${props.buttonSpacing})`};
  margin: ${props => props.buttonSpacing};
  background-color: ${props => props.color} !important;
  opacity: ${props => props.ruptured && !props.isTotem ? 0.5 : 1};
  display: block;
  padding: 0;
`

export const MainContainer = styled.div`
  width: 100%;
  height: 100%;
  padding: 0 0.5vmin;
  font-size: 1.1vmin;
  background-color: ${props => props.showImage && props.theme.navigationBgColor};
  box-shadow: 0.1vh 0.1vh 0.8vh 0.2vh gray;
  border-radius: 5px;
  border-bottom: ${props => props.showSelectedBorderBottom ?
    (`0.7vmin solid ${props.selected ? `${props.theme.pressedBackgroundColor}` : 'transparent !important'}`) : 0};
  border-top: ${props => props.showSelectedBorderBottom ? '0.7vmin solid transparent !important' : 0};
  box-sizing: border-box;
  color: ${props => props.isTotem && props.ruptured ? props.theme.rupturedFontColor : 'unset'};
`

export const QuantityContainer = styled.div`
  display: flex;
  width: 100%;
  height: 100%;
  align-items: center;
  justify-content: flex-end;
`

export const FaIconContainer = styled.div`
  display: flex;
  width: 100%;
  height: 100%;
  align-items: center;
  justify-content: center;
`

export const TextBoxContainer = styled.div`
  display: flex;
  width: 100%;
  height: 100%;
  align-items: center;
  justify-content: center;
  word-break: break-word;
  overflow: hidden;
  color: ${props => props.theme.productFontColor};
`

export const PriceBoxContainer = styled.div`
  display: flex;
  width: 100%;
  height: 100%;
  align-items: flex-end;
  justify-content: flex-end;
`

export const PriceBox = styled.div`
  margin-right: 1vmin;
  font-size: 2.5vmin;
  justify-content: flex-end;
  color: ${props => props.theme.productFontColor};
`

export const ArrowUp = styled.div`
  position: absolute;
  width: 0; 
  height: 0;
  border-left: 1vmin solid transparent;
  border-right: 1vmin solid transparent;
  border-bottom: 1vmin solid ${props => props.theme.pressedBackgroundColor};
  bottom: 0.3vmin;
`

export const ArrowUpContainer = styled.div`
  width: 100%;
  display: flex;
  justify-content: center;
  position: absolute;
  bottom: 0;
`
