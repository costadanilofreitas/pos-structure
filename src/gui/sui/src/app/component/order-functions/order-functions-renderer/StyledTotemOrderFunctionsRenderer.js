import styled from 'styled-components'

export const TotemActionButtonsContainer = styled.div`
  display: flex;
  align-items: center;
  padding: 1vmin 0.5vmin;
  height: calc(100% - 2vmin);
  width: calc(100% - 1vmin);
  background-color: white;
  
  & > * {
    flex: 1;
    margin: 0.5vmin;
    padding: 0.5vmin;
    border-radius: 5px;
  }
`
