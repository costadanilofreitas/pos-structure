const path = require('path')
const webpack = require('webpack')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const ExtractTextPlugin = require('extract-text-webpack-plugin')
const packageJson = require('./package.json')

const extractCSS = new ExtractTextPlugin({ filename: 'styles.css', disable: false, allChunks: true })

module.exports = {
  entry: [
    'babel-polyfill', './src/index.js'
  ],
  output: {
    path: path.join(__dirname, '../../data/server/htdocs/priceInterface'),
    publicPath: '',
    filename: 'bundle.js'
  },
  watch: true,
  watchOptions: {
    ignored: '/node_modules'
  },
  devtool: 'source-map',
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          query: {
            presets: ['react', 'es2015', 'stage-1']
          }
        }
      },
      {
        test: /\.css$/,
        use: extractCSS.extract({
          fallback: 'style-loader',
          use: 'css-loader'
        })
      },
      {
        test: /\.(ttf|otf|eot|svg|woff(2)?)(\?[a-z0-9]+)?$/,
        include: /fonts/,
        exclude: /images/,
        use: {
          loader: 'url-loader?limit=100000&name=fonts/[name].[ext]'
        }
      },
      {
        test: /\.(png|jpg|svg)$/,
        include: /images/,
        exclude: /fonts/,
        use: {
          loader: 'url-loader?limit=100000&name=images/[hash].[ext]'
        }
      }
    ]
  },
  resolve: {
    extensions: ['.js', '.jsx', '.css']
  },
  devServer: {
    historyApiFallback: true,
    contentBase: './'
  },
  plugins: [
    new webpack.DefinePlugin({
      VERSION: JSON.stringify(packageJson.version)
    }),
    new CopyWebpackPlugin([
      { from: 'src/index.html' }
    ]),
    extractCSS
  ]
}
