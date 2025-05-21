import styled from 'styled-components'
import ActionButton from '../component/action-button'

function IconColor(props) {
  if (props.disabled) {
    return props.theme.disabledColor
  }

  if (props.totem) {
    return props.theme.activeColor
  }

  if (props.unselected || props.dialog) {
    return props.theme.unselectIconColor
  }

  if (props.secondaryColor) {
    return props.theme.iconSecondaryColor
  }

  if (props.overrideColor) {
    return props.overrideColor
  }

  return props.theme.iconColor
}

export const IconStyle = styled.i`
  margin: 0.5vmin;
  color: ${props => IconColor(props)};
`

const background = props => props.active ? props.theme.pressedBackgroundColor : props.theme.commonStyledButtonBackground
const color = props => props.active ? props.theme.activeColor : props.theme.commonStyledButtonColor
export const CommonStyledButton = styled(ActionButton)`
  color: ${color} !important;
  border-right: ${props => props.borderRight ? `solid 0.1vmin ${props.theme.backgroundColor} !important` : 'none'};
  border: ${props => props.border ? `solid 0.1vmin ${props.theme.backgroundColor} !important` : 'none'};
  display: ${props => props.flexButton ? 'flex' : 'block'};
  background-color: ${background} !important;
  text-transform: ${props => props.flexButton ? 'uppercase' : 'none'};
`
export const PopupStyledButton = styled(ActionButton)`
  color: ${color} !important;
  border-right: ${props => props.borderRight ? `solid 0.1vmin ${props.theme.backgroundColor} !important` : 'none'};
  border: ${props => props.border ? `solid 0.1vmin ${props.theme.backgroundColor} !important` : 'none'};
  display: ${props => props.flexButton ? 'flex' : 'block'};
  background-color: ${background} !important;
  text-transform: capitalize;
`
