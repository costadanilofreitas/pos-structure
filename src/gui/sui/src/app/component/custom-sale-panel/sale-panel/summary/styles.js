
export default (theme) => ({
  salePanelSummary: {
    composes: 'sale-panel-summary',
    borderTop: '1px solid #cccccc',
    width: '100%',
    height: '100%'
  },
  saleSummarySeparator: {
    composes: 'sale-summary-separator',
    width: '94%',
    margin: '2%',
    borderTop: '1px #cccccc',
    borderTopStyle: 'dashed'
  },
  saleSummaryChangeLine: {
    composes: 'sale-summary-change-line',
    fontSize: '3.2vmin',
    color: '#cd853f'
  },
  saleSummaryTotalLine: {
    composes: 'sale-summary-total-line',
    fontWeight: 'bold',
    color: theme.salePanelFontColor,
    height: props => props.centralizeSummaryTotal ? '100%' : 'none'
  },
  saleSummaryDueLine: {
    composes: 'sale-summary-due-line',
    fontWeight: 'bold'
  }
})
