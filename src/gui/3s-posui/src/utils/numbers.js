export default function ensureDecimals(value, decimalPlaces = 2, decimalSeparator = '.') {
  /**
   * Given a string or number returns a string with the decimals required
   * truncated or filled as needed.
   *
   * Examples:
   * 1 -> "1.00"
   * 1.2 -> "1.20"
   * 1.1278 -> "1.13"
   */
  let currentValue = Number(value).toFixed(decimalPlaces)
  const decimalPlacesInt = parseInt(decimalPlaces, 10)

  if (decimalPlacesInt > 0) {
    // we cannot use toFixed here, because some rounding problems will arise
    currentValue = currentValue.toString()
    currentValue = currentValue.replace('.', decimalSeparator)
    let decimalPos = currentValue.indexOf(decimalSeparator)
    if (decimalPos === -1) {
      currentValue += decimalSeparator
    }
    currentValue += '0'.repeat(decimalPlacesInt)
    decimalPos = currentValue.indexOf(decimalSeparator)
    currentValue = currentValue.slice(0, decimalPos + (decimalPlacesInt + 1))
  }
  return String(currentValue)
}
