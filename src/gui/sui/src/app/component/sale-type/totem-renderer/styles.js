import styled from 'styled-components'

export const ButtonContainer = styled.div`
    padding: 1vmin 0.5vmin;
    height: 100%;
    width: 100%;
    box-sizing: border-box;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: white;
    
    & > * {
      flex: 1;
      border-radius: 5px;
      margin: 0.5vmin;
      padding: 0.5vmin;
      width: 100%;
      height: 100%;
    }
  `
