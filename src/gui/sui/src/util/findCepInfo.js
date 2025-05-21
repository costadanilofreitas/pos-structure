import axios from 'axios'

const BASE_CEP = 'https://viacep.com.br/ws'

function sanitization(cep) {
  const regex = new RegExp(/[^0-9]|[/ /]/g, '')
  const sCep = cep.toString().trim().replace(regex, '')
  if (sCep.length !== 8) {
    throw Error(`Cep: ${cep} inválido!`)
  }
  return sCep
}


export default function findCepInfo(cep) {
  return new Promise((resolve, reject) =>
    axios.get(`${BASE_CEP}/${sanitization(cep)}/json`, {
      headers: {
        'content-type': 'application/json'
      }
    }).then((response) => {
      if (response.erro) {
        reject(Error(`Cep: ${cep} unavailable`))
      }
      return resolve(response.data)
    }).catch(e => {
      console.error(e)
      reject(Error(`Error finding Cep info: ${cep}`))
    })
  )
}

