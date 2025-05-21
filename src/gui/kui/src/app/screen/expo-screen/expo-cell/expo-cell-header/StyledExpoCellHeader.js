import styled, { css, keyframes } from 'styled-components'
import FullContainer from '../../../../styled-components/StyledComponents'


function getBackgroundColor(props) {
  const defaultBgColor = props.selected ? props.theme.activeExpoHeaderCellColor : props.theme.expoHeaderCellColor
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
const ExpoCellContainer = styled(FullContainer)`
  background-color: ${getBackgroundColor};
  color: ${props => props.selected ? props.theme.expoActiveFontColor : props.theme.expoFontColor};
  overflow: hidden;
  text-overflow: ellipsis;
  display: flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
  border-radius: ${props => props.borderRadius};
  ${props => props.blink && props.backgroundColor ? blinkCssBackground : ''}
`

const TitleBlock = styled('div')`
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  text-transform: uppercase;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
`

const OverflowContainer = styled('div')`
  align-items: center;
  justify-content: center;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
`

export { ExpoCellContainer, TitleBlock, OverflowContainer }
