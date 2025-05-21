import styled from 'styled-components'
import ActionButton from '../../../../../../component/action-button'

export const CustomActionButton = styled(ActionButton)`
  box-sizing: border-box;
  margin: 1vmin 0.5vmin;
  border-radius: 5px;
  
  &:first-child {
    margin-left: 1vmin;
  }
  
  &:last-child {
    margin-right: 1vmin;
  }
`
