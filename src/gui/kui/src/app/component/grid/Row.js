import React from 'react'
import PropTypes from 'prop-types'
import styled, { css } from 'styled-components'
import { ensureArray } from '3s-posui/utils'


const notFluidStyling = css `
  margin-bottom: ${({ theme }) => (theme && theme.rowSpace) || 0};

  display: flex;
  justify-content: center;
  align-content: center;
`
const RowRoot = styled.div`
  ${({ fluid }) => fluid ? '' : notFluidStyling};
  display: flex;
`

export default function Row(props) {
  let { children, fluid } = props
  children = ensureArray(children)

  let xsSum = 0

  return (
    <RowRoot fluid={fluid}>
      {children.map((col, idx) => {
        const isFirst = xsSum === 0
        xsSum += col.props.xs
        const isLast = xsSum === 12
        return React.cloneElement(col, { key: idx, isLast: isLast, isFirst: isFirst })
      })}
    </RowRoot>
  )
}

Row.propTypes = {
  children: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
  fluid: PropTypes.bool,
  rowSpace: PropTypes.string,
  className: PropTypes.string
}
