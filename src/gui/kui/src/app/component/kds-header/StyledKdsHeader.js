import styled from 'styled-components'

import FullContainer from '../../styled-components/StyledComponents'

export const KdsHeaderContainer = styled(FullContainer)`
  background-color: gray;
  color: #FFFFFF;
  font-size: 2.5vmin;
`

export const KdsStatisticContainer = styled.div`
  background-color: ${props => props.theme.backgroundColor};
  height: 100%;
  width: 100%;
  font-size: 2vmin;
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
`

export const Goal = styled.div`
  height: 100%;
  color: ${props => props.theme.fontColor};
  font-size: 1.8vmin;
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
`

export const Statistic = styled.div`
  height: 100%;
  color: ${props => props.theme.fontColor};
  font-size: 2vmin;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
`

export const StatisticsValue = styled.span`
  color: ${props => props.isAlert ? '#ff0000' : props.theme.fontColor};
  display: contents;
`

export const OrdersCount = styled.div`
  height: 100%;
  background-color: ${props => props.theme.backgroundColor};
  color: ${props => props.theme.fontColor}; 
  font-size: 2.5vmin;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
`
