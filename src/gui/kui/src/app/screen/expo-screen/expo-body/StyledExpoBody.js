import styled from 'styled-components'


const ExpoBodyContainer = styled('div')`
    height: 100%;
    width: 100%;
    background-color: ${props => props.theme.backgroundColor};
    border-top: ${props => props.theme.defaultBorder};
`

export default ExpoBodyContainer
