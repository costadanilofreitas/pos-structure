import styled, { keyframes, css } from 'styled-components'

import { FlexChild } from '3s-widgets'

const blinkAnimation = (props) => keyframes`
  0% {
    color: ${props.theme.fontColor};
    background-color: ${props.backgroundColor};
  }
  50% {
    color: ${props.theme.activeFontColor};
    background-color: ${props.theme.blinkColor};
  }
`
const blinkAnimationText = (props) => keyframes`
  0% {
    color: ${props.theme.fontColor};
  }
  50% {
    color: ${props.theme.activeFontColor};
  }
`

const blinkCssBackground = (props) => css`
  animation: ${blinkAnimation};
  animation-duration: ${props.theme.animDuration};
  animation-fill-mode: none;
  animation-delay: 0s;
  animation-iteration-count: infinite;
  animation-timing-function: ease-in-out;
  animation-direction: normal;
`

const blinkCssText = (props) => css`
  animation: ${blinkAnimationText};
  animation-duration: ${props.theme.animDuration};
  animation-fill-mode: none;
  animation-delay: 0s;
  animation-iteration-count: infinite;
  animation-timing-function: ease-in-out;
  animation-direction: normal;
`

const ExpoCellContainer = styled('div')`
  height: calc(100% - 1vmin);
  width: ${props => props.widthSize};
  color: ${({ textColor }) => textColor || 'black'};
  font-size: ${props => props.selected ? (props.fontSizeZoom * 1.1) : (props.fontSizeZoom)}vmin;
  margin: 0.1vmin;
  opacity: ${props => props.selected ? '1.0' : '0.8'};
  border-top: ${props => props.theme.expoCellBorder};
  border-bottom: ${props => props.theme.expoCellBorder};
  border-left: ${props => props.withBorder && !props.removeBorderLeft ? props.theme.expoCellBorder : 'none'};
  border-right: ${props => props.withBorder && !props.removeBorderRight ? props.theme.expoCellBorder : 'none'};
  border-bottom-right-radius: ${props => props.withBorder && !props.removeBorderRight ? '1.5vmin' : 'none'};
  border-bottom-left-radius: ${props => props.withBorder && !props.removeBorderLeft ? '1.5vmin' : 'none'};
  border-top-right-radius: ${props => props.withBorder && !props.removeBorderRight ? '1.5vmin' : 'none'};
  border-top-left-radius: ${props => props.withBorder && !props.removeBorderLeft ? '1.5vmin' : 'none'};
  border-color: ${props => props.borderColor};
`

const OrderLines = styled(FlexChild)`
  display: flex;
  flex-direction: column;
  justify-content: center;
`

const CellBodyContainer = styled(FlexChild)`
  display: flex;
  flex-direction: column;
  justify-content: center;
  background-color: ${props => props.backgroundColor};
  ${props => props.blink && props.backgroundColor !== props.theme.expoCellColor ? blinkCssBackground : ''}
`

const OrderLine = styled('p')`
  display: flex;
  width: calc(100% - ${props => 1 + (1.5 * props.level)}vmin);
  align-items: center;
  margin: 0 0 0 ${props => 1.5 * props.level}vmin;
  text-decoration: ${props => props.unavailable || props.delivered ? 'line-through' : ''};
  color: ${props => props.blink && props.backgroundColor !== props.theme.expoCellColor ? '' : props.itemColor};
  flex: 1;
  text-transform: uppercase;
  font-size: ${props => props.isComment ? '70%' : '100%'}; 
  ${props => props.blink && props.backgroundColor !== props.theme.expoCellColor ? blinkCssText : ''}
`

const OrderLineText = styled('span')`
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`

const OrderLineTextComment = styled('span')`
  width: calc(100% - 2.5vmin);
  margin: 0 0 0 1.5vmin;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`

const FaIcon = styled('i')`
  display: flex;
  height: 100%;
  width: 100%;
  align-items: center;
  justify-content: center;
`

const VoidedIcon = styled('i')`
  position: absolute;
  height: 100%;
  width: 100%;
  background-color: ${props => props.theme.voidedCellBackground};
  color: ${props => props.theme.voidedIconColor};
  z-index: 0;
  text-align: center;
  display: flex;
  justify-content: center;
  justify-items: center;
  flex-direction: column;
  font-size: ${props => props.fontSizeZoom * 8}vmin;
`

const AlertIcon = styled('i')`
  position: absolute;
  height: 100%;
  width: 100%;
  background-color: ${props => props.theme.alertCellBackground};
  color: ${props => props.theme.alertIconColor};
  z-index: 0;
  text-align: center;
  display: flex;
  justify-content: center;
  justify-items: center;
  flex-direction: column;
  font-size: ${props => props.fontSizeZoom * 6}vmin;
`

const SaveIcon = styled('i')`
  position: absolute;
  height: 100%;
  width: 100%;
  background-color: ${props => props.theme.alertCellBackground};
  color: ${props => props.theme.saveIconColor};
  z-index: 0;
  text-align: center;
  display: flex;
  justify-content: center;
  justify-items: center;
  flex-direction: column;
  font-size: ${props => props.fontSizeZoom * 7}vmin;
`

const MacroContent = styled('div')`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 100%;
  color: black;
  font-size: ${props => props.fontSizeZoom}vmin;
  background: ${props => props.backgroundColor || props.theme.noItemsCellColor};
`

const DeliveryObservation = styled('div')`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 100%;
  font-size: ${props => props.fontSizeZoom}vmin;
`

export {
  ExpoCellContainer, OrderLines, OrderLine, OrderLineText, FaIcon, VoidedIcon, AlertIcon, SaveIcon, CellBodyContainer,
  MacroContent, OrderLineTextComment, DeliveryObservation
}
