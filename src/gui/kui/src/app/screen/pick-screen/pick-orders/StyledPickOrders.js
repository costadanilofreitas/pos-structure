import styled, { keyframes, css } from 'styled-components'

const blinkAnimation = keyframes`
  0% {
    opacity: 0;
  }
  50% {
    opacity: 100%;
  }
`

const blinkCss = css`
  animation: ${blinkAnimation};
  animation-duration: 1s;
  animation-fill-mode: none;
  animation-delay: 0s;
  animation-iteration-count: 20;
  animation-timing-function: linear;
  animation-direction: normal;
`

export const Container = styled.div`
  display: flex;
  flex-direction: ${({ direction }) => direction ?? 'column'};
  flex: ${props => props.flex ? props.flex : 1};
  width: ${props => props.width || 'unset'};
  height: ${props => props.height || 'unset'};
  align-self: ${props => props.alignSelf || 'unset'};
`

export const OrderInfoBox = styled.div`
  display: flex;
  flex-direction: column;
  background-color: ${props => props.withImage ? 'none' : props.theme.pickupOrderBox};
  border-radius: 2vmin;
  margin: ${props => props.theme.defaultMargin};
  flex: ${props => props.flexGrow ? props.flexGrow : 1};
  justify-content: center;
  align-items: center;
  z-index: 2;
  text-transform: uppercase;
`

export const OrderInfo = styled.div`
  font-family: ${props => props.theme.pickupFontFamily};
  font-size: ${props => props.fontSize}vmin;
  font-weight: bold;
  color: ${props => props.theme.pickupOrderColor};
  margin: 0;
  ${({ blink }) => blink ? blinkCss : ''};
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-align: center;
  position: absolute;
  max-width: ${props => props.maxWidth};
`

export const ReadyOrder = styled.div`
  display: flex;
  font-family: ${props => props.theme.pickupFontFamily};
  font-size: 9vmin;
  font-weight: bold;
  white-space: nowrap;
  color: ${props => props.theme.pickupReadyOrderColor};
  height: 100%;
  justify-content: center;
  align-items: center;
`

export const CalledOrder = styled.div`
  display: flex;
  font-family: ${props => props.theme.pickupFontFamily};
  font-size: 6vmin;
  white-space: nowrap;
  font-weight: bold;
  color: ${props => props.theme.pickupCalledOrderColor};
  height: 100%;
  justify-content: center;
  align-items: center;
`
