import styled from 'styled-components'
import Button from '../../../../../component/action-button/Button'

export const ButtonIcon = styled.div`
  width: 3vh;
`
export const ButtonText = styled.div`
  padding-left: 8px;
  font-size: 1.5em;
`
export const StyledButton = styled(Button)`
  height: calc(100% / 11) !important;
  background-color: ${props => props.theme.backgroundColor};
  flex-basis: calc(100% / 11);
  flex-shrink: 0;
  border: 1px solid ${props => props.theme.screenBackground} !important;`


