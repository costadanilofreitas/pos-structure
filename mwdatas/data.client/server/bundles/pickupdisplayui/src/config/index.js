import devConfig from './index.dev'
import prodConfig from './index.prod'

let config = null;
if(process.env.NODE_ENV === "production") {
    config = prodConfig;
} else {
    config = devConfig;
}

export default config;
