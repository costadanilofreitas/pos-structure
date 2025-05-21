const path = require('path')
const webpack = require('webpack')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const packageJson = require('./package.json')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const OptimizeCSSAssetsPlugin = require('optimize-css-assets-webpack-plugin')
const TerserPlugin = require('terser-webpack-plugin')


module.exports = {
  mode: 'production',
  entry: ['./src/index.js'],
  output: {
    path: path.join(__dirname, '/dist'),
    publicPath: '',
    filename: 'bundle.js'
  },
  devtool: 'source-map',
  watch: false,
  watchOptions: {
    ignored: '/node_modules'
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          query: {
            presets: ['@babel/react', ['@babel/env', { useBuiltIns: 'usage', corejs: 3, modules: false }]],
            plugins: [
              '@babel/plugin-proposal-export-default-from',
              '@babel/plugin-proposal-logical-assignment-operators',
              ['@babel/plugin-proposal-optional-chaining', { 'loose': false }],
              ['@babel/plugin-proposal-pipeline-operator', { 'proposal': 'minimal' }],
              ['@babel/plugin-proposal-nullish-coalescing-operator', { 'loose': false }],
              '@babel/plugin-proposal-do-expressions',
              ['@babel/plugin-proposal-decorators', { 'legacy': true }],
              '@babel/plugin-proposal-function-sent',
              '@babel/plugin-proposal-export-namespace-from',
              '@babel/plugin-proposal-numeric-separator',
              '@babel/plugin-proposal-throw-expressions',
              '@babel/plugin-syntax-dynamic-import',
              '@babel/plugin-syntax-import-meta',
              ['@babel/plugin-proposal-class-properties', { 'loose': true }],
              '@babel/plugin-proposal-json-strings',
              ['babel-plugin-styled-components', { 'displayName': true }]
            ]
          }
        }
      },
      {
        test: /\.s?[ac]ss$/,
        use: [
          MiniCssExtractPlugin.loader,
          { loader: 'css-loader', options: { sourceMap: true } }
        ]
      },
      {
        test: /\.(ttf|otf|eot|svg|woff(2)?)(\?[a-z0-9]+)?$/,
        include: /fonts/,
        exclude: /images/,
        use: {
          loader: 'url-loader',
          options: { limit: 10240, name: 'fonts/[name].[ext]' }
        }
      },
      {
        test: /\.(png|jpg|svg)$/,
        include: /images/,
        exclude: /fonts/,
        use: {
          loader: 'url-loader',
          options: { limit: 10240, name: 'images/[hash].[ext]' }
        }
      },
      {
        test: /\.(ogv|mp4)$/,
        use: [
          {
            loader: 'file-loader',
            options: {
              name: 'images/[hash].[ext]'
            }
          }
        ]
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
  optimization: {
    minimizer: [
      new TerserPlugin({ cache: true, parallel: true, sourceMap: true, terserOptions: { toplevel: true } }),
      new OptimizeCSSAssetsPlugin({})
    ],
    removeAvailableModules: true,
    usedExports: true,
    sideEffects: true
  },
  plugins: [
    new webpack.DefinePlugin({
      VERSION: JSON.stringify(packageJson.version)
    }),
    new CopyWebpackPlugin([
      { from: 'src/index.html' },
      { from: 'static', to: 'static' }
    ]),
    new MiniCssExtractPlugin({ filename: 'styles.css' })
  ]
}
