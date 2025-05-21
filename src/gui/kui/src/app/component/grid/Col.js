import React from 'react'
import PropTypes from 'prop-types'
import styled, { css } from 'styled-components'

const colFlex = css`
  display: flex;
  align-items: center;
`

const ColRoot = styled.div`
  display: inline-block;

  ${({ columnType }) => columnType !== 'LineItemsRenderer' ? colFlex : ''};

  width: ${({ columnWidth }) => columnWidth ?? '100%'};
  font-size: ${({ fontSize }) => fontSize ?? 'unset'};
  flex: ${({ xs }) => xs ?? 'unset'};
`

const ColItem = styled.div`
  height: 100%;
  width: calc(100% - ${({ theme }) => (theme && theme.colSpace) || 0});
  padding-right: calc(${({ theme }) => (theme && theme.colSpace) || 0} / 2);
  padding-left: calc(${({ theme }) => (theme && theme.colSpace) || 0} / 2);

  padding-right: ${({ isLast }) => isLast ? '0 !important' : 'unset'};
  padding-left: ${({ isFirst }) => isFirst ? '0 !important' : 'unset'};

  flex: 1;
`

export default function Col({ children, xs, columnWidth, isLast, isFirst, fontSize, columnType }) {
  return (
    <ColRoot columnType={columnType} columnWidth={columnWidth} xs={xs} fontSize={fontSize}>
      <ColItem isLast={isLast} isFirst={isFirst}>{children}</ColItem>
    </ColRoot>
  )
}

Col.propTypes = {
  children: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
  xs: PropTypes.number,
  columnWidth: PropTypes.number,
  fontSize: PropTypes.string,
  isLast: PropTypes.bool,
  isFirst: PropTypes.bool,
  columnType: PropTypes.string,
  classes: PropTypes.object
}
