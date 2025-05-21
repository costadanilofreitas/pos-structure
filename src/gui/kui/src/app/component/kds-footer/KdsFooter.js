import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { I18N } from '3s-posui/core'

import {
  KdsFooterRoot, KdsFooterContainer, KdsZoomButton, KdsFullClock,
  KdsOrdersCounter, KdsTitle, KdsPaginationBox, ConsolidatedItemsButton,
  PreviousPageIcon, NextPageIcon, KdsUndoIcon, KdsRefreshIcon
} from './StyledKdsFooter'

export default class KdsFooter extends Component {
  shouldComponentUpdate(nextProps) {
    if (this.props.ordersQuantity !== nextProps.ordersQuantity || this.props.ordersTotal !== nextProps.ordersTotal) {
      return true
    }

    if (nextProps.paginationBlockSize !== this.props.paginationBlockSize) {
      return true
    }

    return this.kdsModelWasChanged(this.props.kdsModel, nextProps.kdsModel)
  }
  handleZoomButton = () => {
    return this.props.handleZoom(this.props.selectedView)
  }
  handleUndoButton = () => {
    return this.props.handleUndo(this.props.selectedView)
  }

  render() {
    const {
      showZoomLevel, kdsModel, paginationBlockSize, showUndoButton, handleShowConsolidatedItems,
      handleRefreshScreen, handleGoToPreviousPage, handleGoToNextPage, leftChildren,
      rightChildren, showPagination, showPageNavigation, ordersQuantity, ordersTotal
    } = this.props

    const { cols, rows } = kdsModel.layout
    const cellByPage = (cols * rows)
    const totalPages = Math.ceil(ordersTotal / cellByPage)
    const currentPage = (paginationBlockSize / cellByPage) + 1
    const title = kdsModel.title ? kdsModel.title : kdsModel.viewTitle
    return (
      <KdsFooterRoot>
        <KdsFooterContainer justifyContent="start" className="test_FooterRenderer_LEFT">
          <KdsZoomButton onClick={this.handleZoomButton} className="test_FooterRenderer_ZOOM"/>
          <KdsFullClock/>
          <KdsOrdersCounter>
            <I18N id="$KDS_STATUS_ORDER_COUNTER"/>: {ordersQuantity}&nbsp;&nbsp;
          </KdsOrdersCounter>
          {leftChildren}
        </KdsFooterContainer>

        <KdsFooterContainer justifyContent="center" className="test_FooterRenderer_CENTER">
          <KdsTitle>
            <span>
              <I18N id={`${title}`} defaultMessage={title}/>
            </span>
            {showZoomLevel &&
            <span>
              &nbsp;:: {`${cols}x${rows}`}
            </span>
            }
          </KdsTitle>
        </KdsFooterContainer>

        <KdsFooterContainer justifyContent="end" className="test_FooterRenderer_RIGHT">
          <ConsolidatedItemsButton
            onClick={handleShowConsolidatedItems}
            className="test_FooterRenderer_LIST"
          />
          {rightChildren}
          {showPagination &&
          <KdsPaginationBox className="test_FooterRenderer_PAGINATION">
            <I18N id={'$KDS_PAGE'}/> {currentPage} / {totalPages > 0 ? totalPages : 1}
          </KdsPaginationBox>
          }
          {showPageNavigation &&
          <div>
            <PreviousPageIcon
              onClick={handleGoToPreviousPage}
              disabled={totalPages <= 1}
              className="test_FooterRenderer_PREVIOUS"
            />
            <NextPageIcon
              onClick={handleGoToNextPage}
              disabled={totalPages <= 1}
              className="test_FooterRenderer_NEXT"
            />
          </div>
          }
          {showUndoButton &&
          <KdsUndoIcon onClick={this.handleUndoButton} className="test_FooterRenderer_UNDO"/>
          }
          <KdsRefreshIcon onClick={handleRefreshScreen} className="test_FooterRenderer_REFRESH"/>
        </KdsFooterContainer>
      </KdsFooterRoot>
    )
  }

  kdsModelWasChanged(currentKdsModel, nextKdsModel) {
    if (JSON.stringify(currentKdsModel.layout) !== JSON.stringify(nextKdsModel.layout)) {
      return true
    }

    if (currentKdsModel.title !== nextKdsModel.title) {
      return true
    }

    if (currentKdsModel.viewTitle !== nextKdsModel.viewTitle) {
      return true
    }

    return false
  }
}

KdsFooter.propTypes = {
  kdsModel: PropTypes.object.isRequired,
  paginationBlockSize: PropTypes.number.isRequired,
  handleShowConsolidatedItems: PropTypes.func.isRequired,
  handleRefreshScreen: PropTypes.func.isRequired,
  handleZoom: PropTypes.func.isRequired,
  handleUndo: PropTypes.func.isRequired,
  handleGoToNextPage: PropTypes.func.isRequired,
  handleGoToPreviousPage: PropTypes.func.isRequired,
  showZoomLevel: PropTypes.bool,
  showUndoButton: PropTypes.bool,
  leftChildren: PropTypes.any,
  rightChildren: PropTypes.any,
  showPagination: PropTypes.bool,
  showPageNavigation: PropTypes.bool,
  ordersQuantity: PropTypes.number,
  ordersTotal: PropTypes.number,
  selectedView: PropTypes.object
}

KdsFooter.defaultProps = {
  showZoomLevel: true,
  showUndoButton: true,
  showPagination: false,
  showPageNavigation: false,
  ordersQuantity: 0
}
