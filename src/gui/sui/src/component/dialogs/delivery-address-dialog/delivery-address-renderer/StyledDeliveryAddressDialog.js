import styled from 'styled-components'

import { FlexGrid, FlexChild } from '3s-widgets'

import ActionButton from '../../../action-button'

export const DeliveryAddressBackground = styled.div`
    position: absolute;
    background-color: ${props => props.theme.modalOverlayBackground};
    height: 100%;
    width: 100%;
    z-index: 5;
    display: flex;
    align-items: center;
    justify-content: center;
`
export const DeliveryAddressMainContainer = styled.div`
    position: relative;
    width: 80%;
    height: 100%;
    background: ${props => props.theme.popupsBackgroundColor};
    display: flex;
    flex-direction: column;
`
export const DeliveryAddressKeyboard = styled.div`
    background-color: ${props => props.theme.popupsBackgroundColor};
    text-align: center;
    height: 100%;
    width: 100% - 2 * ${props => props.noInputWrapper ? '0' : '2.5vmin'};
    display: flex;
    font-size: 1.5vmin !important;
    justify-content: center;
    align-items: center;
`
export const DeliveryAddressTitle = styled.div`
    height: 100%;
    flex: 1;
    font-size: 3.0vmin;
    font-weight: bold;
    justify-content: center;
    display: flex;
    align-items: center;
    text-align: center;
    color: ${props => props.theme.pressedColor};
    background-color: ${props => props.theme.pressedBackgroundColor};
 `
export const InputTitle = styled.div`
    height: 100%;
    flex: 1;
    font-size: 1.8vmin;
    font-weight: bold;
    justify-content: center;
    display: flex;
    align-items: center;
    text-align: center;
    color: ${props => props.error ? props.theme.invalidField : 'unset'};
 `
export const AddressInfoContainer = styled(FlexChild)`
    margin: 1vmin;
    height: calc(100% - 2vmin) !important;
    width: calc(100% - 2vmin) !important;
 `
export const InputContainer = styled(FlexGrid)`
    height: 70% !important;
 `
export const BottomButton = styled(ActionButton)`
    flex: 1;
    border: none;
    text-transform: capitalize;
    position: relative;
    display: flex;
    align-items: center;
    height: 100%;
    justify-content: center;
    margin-left: 0;
    &:not(:last-child) {
      border-right: solid 1px #fff;
    }
`
export const SearchButtonContainer = styled(FlexChild)`
    display: flex;
    align-items: center;
    justify-content: center;
`
export const SearchButton = styled.button`
    margin: 0 1vmin;
    width: calc(100% - 2vmin) !important;
    height: 70%;
    background: none;
    border: none;
    color: ${props => props.theme.pressedBackgroundColor};
     &:focus {
      color: ${props => props.theme.iconColor} !important;
    }
`
