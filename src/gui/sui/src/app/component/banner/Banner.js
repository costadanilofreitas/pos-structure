import React, { useEffect, useState } from 'react'
import axios from 'axios'
import BannerRenderer from './banner-renderer/BannerRenderer'

export default function Banner(props) {
  const [bannerConfig, setBannerConfig] = useState({ images: [] })

  useEffect(() => {
    axios.get('/sui/static/totemConfig.json')
      .then(response => response.data)
      .then(data => setBannerConfig(data && data.banner ? data.banner : bannerConfig))
      .catch(e => console.error(e))
  }, [])

  return <BannerRenderer {...props} bannerConfig={bannerConfig} />
}
