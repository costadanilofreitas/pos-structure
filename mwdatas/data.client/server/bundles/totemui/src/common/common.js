export function padZeros(number, amount) {
    number |= 0
    const len = String(number).length - (number < 0 ? 1 : 0 )
    const zeroAmount = amount - len
    if (zeroAmount > 0) {
        if (number >= 0) {
            return "0".repeat(zeroAmount) + number
        } else {
            return "-" + "0".repeat(zeroAmount) + Math.abs(number)
        }
    }
    return number
}