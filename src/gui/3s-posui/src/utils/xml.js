export function parseXml(xmlStr) {
  if (typeof window.DOMParser !== 'undefined') {
    return (new window.DOMParser()).parseFromString(xmlStr, 'text/xml')
  } else if (typeof window.ActiveXObject !== 'undefined') {
    const xmlDoc = new window.ActiveXObject('Microsoft.XMLDOM')
    xmlDoc.async = 'false'
    xmlDoc.loadXML(xmlStr)
    return xmlDoc
  }
  throw new Error('No XML parser found')
}

export function xmlToJson(xml) {
  // Create the return object
  let obj = {}

  if (xml.nodeType === 1) { // element
    // do attributes
    if (xml.attributes.length > 0) {
      obj['@attributes'] = {}
      for (let j = 0; j < xml.attributes.length; j++) {
        const attribute = xml.attributes.item(j)
        obj['@attributes'][attribute.nodeName] = attribute.nodeValue
      }
    }
  } else if (xml.nodeType === 3) { // text
    obj = xml.nodeValue
  } else if (xml.nodeType === 4) { // CDATA
    obj = xml.nodeValue
  }

  // do children
  if (xml.hasChildNodes && xml.hasChildNodes()) {
    for (let i = 0; i < xml.childNodes.length; i++) {
      const item = xml.childNodes.item(i)
      const nodeName = item.nodeName
      if (typeof (obj[nodeName]) === 'undefined') {
        obj[nodeName] = xmlToJson(item)
      } else {
        if (typeof (obj[nodeName].push) === 'undefined') {
          const old = obj[nodeName]
          obj[nodeName] = []
          obj[nodeName].push(old)
        }
        obj[nodeName].push(xmlToJson(item))
      }
    }
  }
  return obj
}

