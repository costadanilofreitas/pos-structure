import styled from 'styled-components'

export const TabContainer = styled.div`
  background-color: gray;
  height: 100%;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
`

export const TabButton = styled.button`
  background-color: ${({ selected, theme }) => selected ? theme.activeBackgroundColor : theme.tabBackgroundColor};
  color: ${({ selected, theme }) => selected ? theme.activeFontColor : theme.fontColor};
  height: 100%;
  width: 100%;
  font-size: 2.5vmin;
  outline: none;
  border-radius: 0;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
`
