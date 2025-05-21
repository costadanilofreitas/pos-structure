import styled, { css, keyframes } from 'styled-components'

import FullContainer from '../../../../styled-components/StyledComponents'

function getBackgroundColor(props) {
  const defaultBgColor = props.selected ? props.theme.activeExpoFooterCellColor : props.theme.expoFooterCellColor
  return props.backgroundColor || defaultBgColor
}

const blinkAnimationBackground = (props) => keyframes`
  0% {
    color: ${props.theme.expoFontColor};
    background-color: ${props.backgroundColor};
  }
  50% {
    color: ${props.theme.expoActiveFontColor};
    background-color: ${props.theme.blinkColor};
  }
`
const blinkCssBackground = (props) => css`
  animation: ${blinkAnimationBackground};
  animation-duration: ${props.theme.animDuration};
  animation-fill-mode: none;
  animation-delay: 0s;
  animation-iteration-count: infinite;
  animation-timing-function: ease-in-out;
  animation-direction: normal;
`

const ExpoCellFooterContainer = styled(FullContainer)`
    background-color: ${getBackgroundColor};
    color: ${props => {
    if (getBackgroundColor(props) === props.theme.activeExpoCellColor) {
      return props.theme.expoActiveFontColor
    }
    return props.theme.expoFontColor
  }};
    overflow: hidden;
    text-overflow: ellipsis;
    display: flex;
    align-items: center;
    justify-content: center;
    white-space: pre;
    border-radius: ${props => props.borderRadius};
    text-transform: uppercase;
    padding: 0 1vmin;
    width: calc(100% - 2vmin);
    ${props => props.blink && props.backgroundColor ? blinkCssBackground : ''}
`

const OverflowContainer = styled('div')`
    align-items: center;
    justify-content: center;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
`

export { ExpoCellFooterContainer, OverflowContainer }
