import styled from 'styled-components'


const GridContainer = styled('div')`
  width: 100%;
  height: 100%;
  display: flex;
`;

const ChildContainer = styled('div')`
  position: relative !important;
`;

const AbsoluteWrapper = styled('div')`
  width: 100%;
  height: 100%;
  position: absolute;
`;

export { GridContainer, ChildContainer, AbsoluteWrapper }
