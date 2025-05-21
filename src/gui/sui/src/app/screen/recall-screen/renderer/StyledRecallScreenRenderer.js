import styled, { keyframes } from 'styled-components'
import Button from '../../../../component/action-button/Button'

export const StyledButton = styled(Button)`
    flex-grow: 1;
    flex-shrink: 0;
    flex-basis: 0;
    padding: 1px;
    text-transform: uppercase;
    background-color: ${props => props.theme.backgroundColor};
    color: ${props => props.theme.fontColor};
    font-Size: ${props => props.submenuActive ? '1.4vh' : '1.3vh'} !important;
    font-weight: ${props => props.submenuActive ? 'bold' : 'normal'};
    border-bottom: 5px solid ${props => props.submenuActive ?
    props.theme.pressedBackgroundColor :
    `${props.theme.screenBackground} !important`};
    position: unset;
`

const spin = keyframes`
   from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
`

export const SpinningIcon = styled.i`
  animation: ${spin} 2s linear ${props => props.spin ? 'infinite' : '0'};
`
