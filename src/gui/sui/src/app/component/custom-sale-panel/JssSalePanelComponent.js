import injectSheet from 'react-jss'
import SalePanelComponent from './SalePanelComponent'

const styles = (theme) => ({
  salePanel: {
    backgroundColor: props => props.salePanelBackground ? theme.salePanelBackgroundColor : 'none',
    border: 'none !important',
    height: '100%',
    width: '100%',
    '& .sale-panel-item-root.selected': {
      backgroundColor: theme.pressedBackgroundColor
    },
    '& .scroll-panel-items>div:last-child .sale-panel-item-level0.selected': {
      fontSize: '2vmin',
      fontWeight: 'bold'
    },
    '& .sale-panel-item-level1.selected, .sale-panel-item-level2.selected, .sale-panel-item-level3.selected': {
      backgroundColor: theme.activeBackgroundColor,
      color: theme.selectedProductFontColor
    },
    '& .sale-panel-item-comment-level1, .sale-panel-item-comment-level2, .sale-panel-item-comment-level3': {
      backgroundColor: theme.salePanelBackgroundColor,
      color: theme.productFontColor,
      marginLeft: '4%',
      fontStyle: 'italic',
      fontSize: '1.2vmin'
    },
    '& .sale-panel-item-hold, .sale-panel-item-fire, .sale-panel-item-dont-make': {
      width: '60%',
      color: 'inherit'
    }
  },
  customerNameLine: {
    fontSize: '1.5vh',
    paddingTop: '0.4vmin',
    textOverflow: 'ellipsis',
    overflow: 'hidden',
    whiteSpace: 'nowrap'
  }
})

export default injectSheet(styles)(SalePanelComponent)
