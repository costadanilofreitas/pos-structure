const styles = (theme) => ({
  salePanelItemRoot: {
    composes: 'sale-panel-item-root',
    padding: '0.5vmin',
    display: 'flex',
    justifyContent: 'space-between',
    position: 'relative',
    fontWeight: props => props.biggerFont ? 'bold' : 'none',
    fontSize: props => props.biggerFont ? '2vmin' : 'none'
  },
  salePanelItemSeparator: {
    composes: 'sale-panel-item-separator',
    width: '92%',
    borderTop: '1px solid #ccc',
    position: 'absolute',
    left: '2%'
  },
  salePanelItemLevel0: {
    composes: 'sale-panel-item-level0',
    paddingLeft: '2%',
    paddingRight: '2%',
    '&.selected': {
      fontSize: '2vmin',
      fontWeight: 'bold',
      backgroundColor: 'black',
      color: 'white'
    }
  },
  salePanelItemLevel1: {
    composes: 'sale-panel-item-level1',
    paddingLeft: '5%',
    paddingRight: '2%',
    '&.selected': {
      backgroundColor: '#1752ff',
      color: 'white'
    }
  },
  salePanelItemLevel2: {
    composes: 'sale-panel-item-level2',
    paddingLeft: '9%',
    paddingRight: '2%'
  },
  salePanelItemLevel3: {
    composes: 'sale-panel-item-level3',
    paddingLeft: '13%',
    paddingRight: '2%'
  },
  salePanelItemLevel4: {
    composes: 'sale-panel-item-level4',
    paddingLeft: '17%',
    paddingRight: '2%'
  },
  salePanelItemLevel5: {
    composes: 'sale-panel-item-level5',
    paddingLeft: '21%',
    paddingRight: '2%'
  },
  salePanelItemModifier: {
    composes: 'sale-panel-item-modifier',
    color: theme.productColor
  },
  salePanelItemDesc: {
    composes: 'sale-panel-item-desc',
    whiteSpace: 'pre',
    overflow: 'hidden',
    fontSize: '2vmin',
    textOverflow: 'ellipsis',
    paddingLeft: '1%',
    width: '100%',
    backgroundColor: 'transparent !important'
  },
  salePanelItemPrice: {
    composes: 'sale-panel-item-price',
    paddingRight: '2%',
    paddingLeft: '2%',
    fontSize: '2vmin',
    backgroundColor: 'transparent !important',
    textAlign: 'right'
  },
  salePanelItemPriceDiscount: {
    composes: 'sale-panel-item-price-discount',
    color: '#f57c00'
  },
  salePanelItemCommentLevel0: {
    composes: 'sale-panel-item-comment-level0',
    backgroundColor: '#FFECB3',
    paddingLeft: '2%',
    paddingRight: '2%'
  },
  salePanelItemCommentLevel1: {
    composes: 'sale-panel-item-comment-level1',
    backgroundColor: '#FFECB3',
    paddingLeft: '5%',
    paddingRight: '2%'
  },
  salePanelItemCommentLevel2: {
    composes: 'sale-panel-item-comment-level2',
    backgroundColor: '#FFECB3',
    paddingLeft: '9%',
    paddingRight: '2%'
  },
  salePanelItemCommentLevel3: {
    composes: 'sale-panel-item-comment-level3',
    backgroundColor: '#FFECB3',
    paddingLeft: '13%',
    paddingRight: '2%'
  },
  salePanelItemNegativePrice: {
    composes: 'sale-panel-item-negative-price',
    color: '#ff0000'
  },
  salePanelItemOpenOption: {
    composes: 'sale-panel-item-open-option',
    backgroundColor: '#ffff00 !important',
    padding: '2px',
    margin: '-2px',
    width: 'auto',
    marginRight: 'auto'
  },
  salePanelItemNotRequiredOption: {
    composes: 'sale-panel-item-not-required-option',
    backgroundColor: theme.salePanelItemNotRequiredOption,
    color: theme.salePanelItemsColor
  },
  salePanelItemIcon: {
    width: '100%',
    textAlign: 'center'
  },
  salePanelItemSeat: {
    composes: 'sale-panel-item-seat',
    width: '6%'
  },
  salePanelItemIconContainer: {
    display: 'flex',
    width: '6%',
    minWidth: '6%'
  },
  salePanelItemMandatoryOption: {
    composes: 'sale-panel-item-mandatory-option',
    backgroundColor: theme.salePanelItemMandatoryOption,
    color: theme.salePanelItemsColor
  }
})

export default styles
