import styled, { css } from 'styled-components'

const selectedEffect = css`
  font-style: italic;
  border: 5px solid #7FFF00;
`

const containerThresholds = [
  css`
    background-color: ${({ theme }) => (theme && theme.line && theme.line.backgroundColor) ?? 'unset'};
    border-color: ${({ theme }) => (theme && theme.line && theme.line.backgroundColor) ?? 'unset'};
    padding:  ${({ selected }) => selected ? '0px' : '5px'};
    color: ${({ theme }) => (theme && theme.line && theme.line.color) ?? 'unset'};
`,
  css`
    background-color: ${({ selected }) => selected ? 'rgb(242, 227, 148)' : 'rgba(242, 227, 148, 0.7)'};
    border: 5px solid ${({ selected }) => selected ? 'rgb(242, 227, 148)' : 'rgba(242, 227, 148, 0.7)'};
    color: black;
  `,
  css`
    background-color: ${({ selected }) => selected ? 'rgb(242, 227, 148)' : 'rgba(242, 227, 148, 0.7)'};
    border: 5px solid ${({ selected }) => selected ? 'rgb(242, 227, 148)' : 'rgba(242, 227, 148, 0.7)'};
    color: black;
  `,
  css`
    background-color: ${({ selected }) => selected ? 'rgb(255, 000, 000)' : 'rgba(255, 000, 000, 0.7)'};
    border: 5px solid ${({ selected }) => selected ? 'rgb(255, 000, 000)' : 'rgba(255, 000, 000, 0.7)'};
    color: black;
  `
]

export const Container = styled.div`
  outline: 1px solid black;
  ${({ threshold }) => containerThresholds[threshold]};
  ${({ selected }) => selected ? selectedEffect : ''};
  
  display: flex;
  flex-direction: row;
`

export const ContentContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0.5vmin;
  flex: ${({ width }) => width ?? '1'};
`
