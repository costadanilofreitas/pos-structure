import styled from 'styled-components'
import Button from '../../../../component/action-button/Button'

export const ContainerStyle = styled.div`
  display: flex;
  width: 100%;
  height: 100%;
`
export const ButtonStyle = styled(Button)`
  flex: 1;
  background-color: ${props => props.theme.backgroundColor};
  box-sizing: border-box;
  border-bottom: ${props => props.selected ? `0.7vmin solid ${props.theme.pressedBackgroundColor}` : '0.7vmin solid transparent'};
  border-top: 0.7vmin solid transparent;
  position: unset;
`
