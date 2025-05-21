const prepColumns = [
  {
    id: 1,
    title: '$KDS_PREP_ORDER',
    renderer: 'LineValueRenderer',
    path: 'orderData.attributes.id',
    size: 1,
    style: {
      justifyContent: 'center'
    }
  },
  {
    id: 2,
    title: '$KDS_PREP_TABLE',
    renderer: 'TableNumberRenderer',
    size: 1,
    style: {
      justifyContent: 'center'
    }
  },
  {
    id: 3,
    title: '$KDS_PREP_SALE_TYPE',
    renderer: 'LineSaleTypeRenderer',
    size: 1,
    style: {
      justifyContent: 'center'
    }
  },
  {
    id: 4,
    title: '$KDS_PREP_TIME',
    renderer: 'LineAgeRenderer',
    size: 1,
    style: {
      justifyContent: 'center'
    }
  },
  {
    id: 5,
    title: '$KDS_PREP_COOK',
    renderer: 'LineCookTimeRenderer',
    size: 1,
    style: {
      justifyContent: 'center'
    }
  },
  {
    id: 6,
    title: '$KDS_PREP_ITEM',
    renderer: 'LineItemsRenderer',
    maxColumns: 3,
    size: 8,
    style: {
      justifyContent: 'center'
    }
  },
  {
    id: 7,
    title: '$ACTIONS',
    renderer: 'LineActionsRenderer',
    size: 2,
    style: {
      justifyContent: 'center'
    }
  }
]

export default prepColumns
