import injectSheet from 'react-jss'

export function injectMultipleSheet(...styles) {
  const styleFunction = (theme) => {
    let finalStyle = styles[0](theme)
    styles.slice(1).forEach(specificStyle => {
      finalStyle = Object.assign(finalStyle, specificStyle(theme))
    })

    return finalStyle
  }

  return injectSheet(styleFunction)
}
