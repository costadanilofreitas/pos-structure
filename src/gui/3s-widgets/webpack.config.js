const path = require('path')
const webpack = require('webpack')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const packageJson = require('./package.json')
const TerserPlugin = require('terser-webpack-plugin')


module.exports = {
  mode: 'production',
  entry: { main: './index.js' },
  output: {
    path: path.join(__dirname, '/lib'),
    filename: 'index.js',
    library: '3s-widgets',
    libraryTarget: 'umd'
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules|style/,
        use: {
          loader: 'babel-loader',
          query: {
            presets: ['@babel/react', ['@babel/env', { useBuiltIns: 'usage', corejs: 3 }]],
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
              '@babel/plugin-proposal-json-strings'
            ]
          }
        }
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
  externals: [
    'react',
    'react-dom',
    'lodash',
    'prop-types',
    'react-redux',
    'react-jss'
  ],
  resolve: {
    extensions: ['.js', '.jsx', '.css']
  },
  devServer: {
    historyApiFallback: true,
    contentBase: './'
  },
  optimization: {
    minimizer: [new TerserPlugin({ cache: true, parallel: true, sourceMap: true, terserOptions: { toplevel: true } })],
    removeAvailableModules: true,
    usedExports: true,
    sideEffects: false
  },
  plugins: [
    new webpack.DefinePlugin({
      VERSION: JSON.stringify(packageJson.version)
    }),
    new CopyWebpackPlugin([
      { from: './package.json' }
    ])
  ]
}
