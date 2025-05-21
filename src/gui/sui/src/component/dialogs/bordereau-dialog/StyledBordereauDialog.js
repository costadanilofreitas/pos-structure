import styled, { css, keyframes } from 'styled-components'

const blinkAnimationBackground = (props) => keyframes`
  50% {
    background: ${props.theme.dialogTitleBackgroundColor};
    color: ${props.theme.popupsBackgroundColor};
  }
`

const blinkCssBackground = () => css`
  animation: ${blinkAnimationBackground};
  animation-duration: 1s;
  animation-fill-mode: none;
  animation-delay: 0s;
  animation-iteration-count: infinite;
  animation-timing-function: ease-in-out;
  animation-direction: normal;
`

const BordereauValue = styled.div`
  width: calc(100%/${props => props.columns});
  height: calc(100%/${props => props.rows});
  ${props => props.blink ? blinkCssBackground : ''};
`

const BordereauItemInfoCheckBox = styled.div`
  font-size: 2vmin;
`

export { BordereauValue, BordereauItemInfoCheckBox }
