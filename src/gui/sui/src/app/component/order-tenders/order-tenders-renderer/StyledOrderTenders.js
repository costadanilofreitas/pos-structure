import styled from 'styled-components'
import ActionButton from '../../../../component/action-button'

export const TotemButton = styled(ActionButton)`
  opacity: 0.9;
  align-self: center;
  
  height: 20vmin;
  width: 20vmin;
  
  border-radius: 2vmin;
  margin: 1vmin;
  
  display: flex;
  flex-direction: column;
  justify-content: center;
  
  & > i {
    margin-top: 1vmin;
    font-size: 4.5vmin;
  }
`
export const TotemTenderText = styled.div`
  font-size: 3vmin;
  font-family: Roboto, Work Sans, Regular, Verdana, Arial, sans-serif;
  font-weight: 600;
  color: #FFF;
  text-align: center;
`

export const TotemButtonGrid = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-evenly;
  align-items: center;
  width: 100%;
  
  margin: auto;
`
