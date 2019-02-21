const webpack = require('webpack')
const ExtractTextPlugin = require('extract-text-webpack-plugin')

module.exports = {
    entry: ['babel-polyfill', './src/index.jsx'],
    output: {
        path: __dirname + '/build',
        filename: './app.js'
    },
    devServer: {
        port: 8083,
        contentBase: './build',
        proxy: {
            '/totem': {
                target: 'http://localhost:8080/'
            }
        }
    },
    resolve: {
        extensions: ['', '.js', '.jsx'],
        alias: {
            modules: __dirname + '/node_modules'
        }
    },
    plugins: [
        new webpack.ProvidePlugin({
            $: "jquery",
            jquery: "jquery",
            "window.jQuery": "jquery",
            jQuery: "jquery"
        }),
        new ExtractTextPlugin('app.css')
    ],
    module: {
        loaders: [{
            test: /.js[x]?$/,
            loader: 'babel-loader',
            exclude: /node_modules/,
            query: {
                presets: ['es2015', 'react', 'stage-1'],
                plugins: ['transform-object-rest-spread']
            }
        }, {
            test: /bootstrap.+\.(jsx|js)$/,
            loader: 'imports?jQuery=jquery,$=jquery,this=>window'
        }, {
            test: /\.css$/,
            loader: ExtractTextPlugin.extract('style-loader', 'css-loader')
        }, {
            test: /\.woff|.woff2|.ttf|.eot|.otf|.svg|.png|.jpg*.*$/,
            loader: require.resolve("file-loader") + "?name=[path][name].[ext]"
        }]
    }
}