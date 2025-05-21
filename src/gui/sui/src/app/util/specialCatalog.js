export function getPriceList(specialCatalog, selectedTable) {
  let tableCatalog
  if (selectedTable && selectedTable.specialCatalog) {
    tableCatalog = selectedTable.specialCatalog
  } else {
    tableCatalog = ''
  }

  let listSpecialCatalog = ''
  if (tableCatalog) {
    if (specialCatalog) {
      listSpecialCatalog = specialCatalog.concat('.')
    }
    listSpecialCatalog = listSpecialCatalog.concat(tableCatalog)
  } else {
    listSpecialCatalog = specialCatalog
  }
  return listSpecialCatalog
}
