const path = require('path')
const webpack = require('webpack')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const packageJson = require('./package.json')
const TerserPlugin = require('terser-webpack-plugin')


module.exports = {
  mode: 'production',
  entry: {
    'core/IntlProviderContainer.js': './src/core/IntlProviderContainer.js',
    'core/executeSaga.js': './src/core/executeSaga.js',
    'core/ThemeProviderContainer.js': './src/core/ThemeProviderContainer.js',
    'core/index.js': './src/core/index.js',
    'core/loggingMiddleware.js': './src/core/loggingMiddleware.js',
    'core/i18nSaga.js': './src/core/i18nSaga.js',
    'core/globalTimerMiddleware.js': './src/core/globalTimerMiddleware.js',
    'core/I18N.js': './src/core/I18N.js',
    'core/MessageBus.js': './src/core/MessageBus.js',
    'constants/config.js': './src/constants/config.js',
    'constants/actionTypes.js': './src/constants/actionTypes.js',
    'utils/order.js': './src/utils/order.js',
    'utils/AutoFocusComponent.js': './src/utils/AutoFocusComponent.js',
    'utils/numbers.js': './src/utils/numbers.js',
    'utils/xml.js': './src/utils/xml.js',
    'utils/index.js': './src/utils/index.js',
    'utils/saga.js': './src/utils/saga.js',
    'utils/prod.js': './src/utils/prod.js',
    'utils/date.js': './src/utils/date.js',
    'utils/helper.js': './src/utils/helper.js',
    'button/index.js': './src/button/index.js',
    'button/Button.js': './src/button/Button.js',
    'actions/dismissInfoMessageAction.js': './src/actions/dismissInfoMessageAction.js',
    'actions/buttonDownAction.js': './src/actions/buttonDownAction.js',
    'actions/showInfoMessageAction.js': './src/actions/showInfoMessageAction.js',
    'actions/index.js': './src/actions/index.js',
    'actions/setThemeAction.js': './src/actions/setThemeAction.js',
    'actions/buttonUpAction.js': './src/actions/buttonUpAction.js',
    'actions/bumpAction.js': './src/actions/bumpAction.js',
    'actions/setLanguageAction.js': './src/actions/setLanguageAction.js',
    'actions/executeAction.js': './src/actions/executeAction.js',
    'reducers/recallDataReducer.js': './src/reducers/recallDataReducer.js',
    'reducers/posStateReducer.js': './src/reducers/posStateReducer.js',
    'reducers/themeReducer.js': './src/reducers/themeReducer.js',
    'reducers/localeReducer.js': './src/reducers/localeReducer.js',
    'reducers/index.js': './src/reducers/index.js',
    'reducers/orderLastTimestampReducer.js': './src/reducers/orderLastTimestampReducer.js',
    'reducers/drawerStateReducer.js': './src/reducers/drawerStateReducer.js',
    'reducers/drawerOpenedReducer.js': './src/reducers/drawerOpenedReducer.js',
    'reducers/posIdReducer.js': './src/reducers/posIdReducer.js',
    'reducers/workingModeReducer.js': './src/reducers/workingModeReducer.js',
    'reducers/mwActionReducer.js': './src/reducers/mwActionReducer.js',
    'reducers/trainingModeReducer.js': './src/reducers/trainingModeReducer.js',
    'reducers/infoMessageReducer.js': './src/reducers/infoMessageReducer.js',
    'reducers/dimensionsReducer.js': './src/reducers/dimensionsReducer.js',
    'reducers/timeDeltaReducer.js': './src/reducers/timeDeltaReducer.js',
    'reducers/kdsIdReducer.js': './src/reducers/kdsIdReducer.js',
    'reducers/customModelReducer.js': './src/reducers/customModelReducer.js',
    'reducers/dialogsReducer.js': './src/reducers/dialogsReducer.js',
    'reducers/orderReducer.js': './src/reducers/orderReducer.js',
    'reducers/loadingReducer.js': './src/reducers/loadingReducer.js',
    'reducers/codIdReducer.js': './src/reducers/codIdReducer.js',
    'reducers/prodOrdersReducer.js': './src/reducers/prodOrdersReducer.js',
    'reducers/buildsReducer.js': './src/reducers/buildsReducer.js',
    'reducers/globalTimerReducer.js': './src/reducers/globalTimerReducer.js',
    'widgets/LoadingScreen.js': './src/widgets/LoadingScreen.js',
    'widgets/Clock.js': './src/widgets/Clock.js',
    'widgets/StartupWarning.js': './src/widgets/StartupWarning.js',
    'widgets/ScreenSize.js': './src/widgets/ScreenSize.js',
    'widgets/index.js': './src/widgets/index.js',
    'widgets/ContextButton.js': './src/widgets/ContextButton.js',
    'widgets/DataTable.js': './src/widgets/DataTable.js',
    'widgets/InfoMessage.js': './src/widgets/InfoMessage.js',
    'widgets/KDSCellTimer.js': './src/widgets/KDSCellTimer.js',
    'widgets/ContextMenu.js': './src/widgets/ContextMenu.js',
    'widgets/OrderTimer.js': './src/widgets/OrderTimer.js',
    'keyboard/KeyboardButton.js': './src/keyboard/KeyboardButton.js',
    'keyboard/index.js': './src/keyboard/index.js',
    'keyboard/Keyboard.js': './src/keyboard/Keyboard.js',
    'keyboard/KeyboardInput.js': './src/keyboard/KeyboardInput.js',
    'keyboard/layouts/LatinLayout.js': './src/keyboard/layouts/LatinLayout.js',
    'keyboard/layouts/CyrillicLayout.js': './src/keyboard/layouts/CyrillicLayout.js',
    'keyboard/layouts/SymbolsLayout.js': './src/keyboard/layouts/SymbolsLayout.js',
    'keyboard/icons/BackspaceIcon.js': './src/keyboard/icons/BackspaceIcon.js',
    'keyboard/icons/ShiftIcon.js': './src/keyboard/icons/ShiftIcon.js',
    'keyboard/icons/LanguageIcon.js': './src/keyboard/icons/LanguageIcon.js'
  },
  output: {
    path: path.join(__dirname, '/lib'),
    filename: '[name]',
    library: '3s-posui',
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
    /^3s-posui\/.+$/,
    'react',
    'react-dom',
    'lodash',
    'axios',
    'prop-types',
    'react-modal-dialog',
    /^redux-saga\/.+$/,
    'redux',
    'react-redux',
    'react-intl',
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
      {
        from: './package.json',
        transform: (content) =>
          content.toString().replace(
            /\s+"optionalDependencies": {\s+"posui": "file:\."\s+},/,
            ''
          )
      }
    ])
  ]
}
